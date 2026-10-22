// CPU-only bounded native draft. No HTTP, provider, database or app credentials.
#include "llama.h"
#include <jni.h>
#include <cstdio>
#include <unistd.h>
#include <sys/stat.h>
#include <chrono>
#include <memory>
#include <string>
#include <vector>

using Clock=std::chrono::steady_clock;
static bool expired(void * value) { return Clock::now()-*static_cast<Clock::time_point*>(value)>std::chrono::seconds(20); }
static bool progress(float, void * value) { return !expired(value); }
static void silent(enum ggml_log_level,const char*,void*) {}

extern "C" JNIEXPORT jbyteArray JNICALL
Java_dev_ada_assistant_edge_NativeDraftBridge_generate(JNIEnv * env,jobject,jint fd,jbyteArray input) {
    try {
        struct stat info{};
        if(fstat(fd,&info)!=0 || (info.st_size!=386404992 && info.st_size!=639446688)) throw 1;
        const int length=env->GetArrayLength(input);
        if(length<1 || length>2000) throw 1;
        std::string prompt(length,'\0');env->GetByteArrayRegion(input,0,length,reinterpret_cast<jbyte*>(prompt.data()));
        auto started=Clock::now();llama_log_set(silent,nullptr);llama_backend_init();
        auto params=llama_model_default_params();params.n_gpu_layers=0;params.progress_callback=progress;params.progress_callback_user_data=&started;
        std::unique_ptr<FILE,decltype(&fclose)> file(fdopen(dup(fd),"rb"),fclose);
        if(!file) throw 1;
        std::unique_ptr<llama_model,decltype(&llama_model_free)> model(llama_model_load_from_file_ptr(file.get(),params),llama_model_free);
        if(!model || expired(&started)) throw 1;
        const auto * vocab=llama_model_get_vocab(model.get());
        int count=-llama_tokenize(vocab,prompt.data(),length,nullptr,0,true,true);
        if(count<1 || count>384) throw 1;
        std::vector<llama_token> tokens(count);
        if(llama_tokenize(vocab,prompt.data(),length,tokens.data(),count,true,true)<0) throw 1;
        auto settings=llama_context_default_params();settings.n_ctx=512;settings.n_batch=512;settings.n_ubatch=64;settings.n_threads=2;settings.n_threads_batch=2;settings.no_perf=true;
        std::unique_ptr<llama_context,decltype(&llama_free)> ctx(llama_init_from_model(model.get(),settings),llama_free);
        if(!ctx) throw 1;
        llama_set_abort_callback(ctx.get(),expired,&started);
        // Fixed decoding; benchmark and review the same bounded path. No tools or hidden history.
        std::unique_ptr<llama_sampler,decltype(&llama_sampler_free)> sampler(llama_sampler_init_greedy(),llama_sampler_free);
        if(llama_decode(ctx.get(),llama_batch_get_one(tokens.data(),count))!=0) throw 1;
        std::string output;bool complete=false;
        for(int i=0;i<64;i++) {
            if(expired(&started)) throw 1;
            auto token=llama_sampler_sample(sampler.get(),ctx.get(),-1);
            if(llama_vocab_is_eog(vocab,token)){complete=true;break;}
            char piece[512];int size=llama_token_to_piece(vocab,token,piece,sizeof(piece),0,false);
            if(size<0 || size>512 || output.size()+size>12000) throw 1;
            output.append(piece,size);
            if(llama_decode(ctx.get(),llama_batch_get_one(&token,1))!=0) throw 1;
        }
        if(output.empty()) throw 1;
        auto result=env->NewByteArray(output.size()+1);jbyte flag=complete?1:0;
        env->SetByteArrayRegion(result,0,1,&flag);
        env->SetByteArrayRegion(result,1,output.size(),reinterpret_cast<const jbyte*>(output.data()));
        return result;
    } catch(...) {
        env->ThrowNew(env->FindClass("java/io/IOException"),"Local draft unavailable or resource limit reached");return nullptr;
    }
}
