import { useId, type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode } from 'react';

export function Button({ secondary = false, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { secondary?: boolean }) {
  return <button className={secondary ? 'button button-secondary' : 'button'} {...props} />;
}
export function Field({ label, hint, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string; hint?: string }) {
  const id = useId();
  return <div className="field"><label htmlFor={id}>{label}</label><input id={id} aria-describedby={hint ? `${id}-hint` : undefined} {...props} />{hint && <p className="hint" id={`${id}-hint`}>{hint}</p>}</div>;
}
export function Panel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={`panel ${className}`}>{children}</section>;
}
export function TextContent({ text }: { text: string }) {
  return <p className="untrusted-text">{text}</p>;
}
export function safeHref(value: string): string | undefined {
  try {
    const url = new URL(value);
    return ['https:', 'http:'].includes(url.protocol) && !url.username && !url.password ? url.href : undefined;
  } catch { return undefined; }
}
