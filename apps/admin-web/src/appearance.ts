export type Appearance = { palette: 'blue' | 'red' | 'olive'; mode: 'system' | 'light' | 'dark'; text: 'standard' | 'large' };
export const appearanceKey = 'ada.appearance.v1';
export function loadAppearance(): Appearance {
  try {
    const value = JSON.parse(localStorage.getItem(appearanceKey) ?? '{}');
    return { palette: ['blue', 'red', 'olive'].includes(value.palette) ? value.palette : 'blue', mode: ['system', 'light', 'dark'].includes(value.mode) ? value.mode : 'system', text: value.text === 'large' ? 'large' : 'standard' };
  } catch { return { palette: 'blue', mode: 'system', text: 'standard' }; }
}
export function saveAppearance(value: Appearance) {
  try { localStorage.setItem(appearanceKey, JSON.stringify({ palette: value.palette, mode: value.mode, text: value.text })); } catch { /* Appearance still applies when storage is disabled. */ }
}
