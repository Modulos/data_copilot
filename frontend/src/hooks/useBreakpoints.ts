import { useMediaQuery } from '@vueuse/core';

export default function useBreakpoints() {
  const isMobile = useMediaQuery('(max-width: 600px)');

  return { isMobile };
}
