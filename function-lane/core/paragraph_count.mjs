export function countParagraphs(text = "") {
  const value = String(text).trim();
  if (!value) return 0;
  return value.split(/\n\s*\n/u).filter(part => part.trim()).length;
}

export function paragraphResultFor(text = "") {
  return { paragraphs: countParagraphs(text) };
}
