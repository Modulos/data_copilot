import { onMounted, onUnmounted } from 'vue';

export default function useScrollUp(callback?: Function, ...args: any[]) {
  function onscroll() {
    const topOfWindow = document.documentElement.scrollTop === 0;
    if (topOfWindow && callback) {
      callback(...args);
    }
  }
  onMounted(() => {
    window.addEventListener('scroll', onscroll);
  });

  onUnmounted(() => {
    window.removeEventListener('scroll', onscroll);
  });
}
