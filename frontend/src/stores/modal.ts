import { defineStore } from 'pinia';

interface State {
  isActive: boolean;
  callback: Function | null;
  args: any[];
  title: string;
  description: string;
}

const useModalStore = defineStore({
  id: 'modal',
  state: (): State => ({
    isActive: false,
    callback: null,
    args: [],
    title: '',
    description: '',
  }),
  actions: {

    fillModal(title: string, description: string) {
      this.title = title;
      this.description = description;
    },

    openModal(cb: Function, ...params: any[]) {
      this.callback = cb;
      this.isActive = true;
      this.args = params;
    },

    closeModal() {
      this.title = '';
      this.description = '';
      this.isActive = false;
      this.callback = null;
      this.args = [];
    },

    async confirm() {
      if (this.callback) {
        await this.callback(...this.args);
      }
      this.closeModal();
      console.log(this);
    },

  },
});

export default useModalStore;
