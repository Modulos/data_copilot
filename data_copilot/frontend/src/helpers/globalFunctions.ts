export default function getFirstLetters(string = '') {
  const firstChars = string
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase());

  return firstChars.join(' ');
}
