export function sanitizeText(value = "") {
  return String(value).replace(/[<>]/g, "");
}
