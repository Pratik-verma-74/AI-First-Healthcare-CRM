import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { FormStateDTO } from '../services/api';

interface InteractionState {
  currentFormData: FormStateDTO;
  interactionList: any[];
  activeInteractionId: number | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialFormState: FormStateDTO = {
  hcp_name: '',
  hospital: '',
  interaction_type: 'Meeting',
  date: new Date().toISOString().split('T')[0],
  time: '12:00',
  attendees: 'Medical Representative',
  topics_discussed: '',
  materials_shared: 'No materials attached',
  samples_distributed: 'No samples distributed',
  observed_sentiment: 'Neutral',
  outcomes: '',
  follow_up_actions: '',
  ai_summary: '',
  status: 'Draft'
};

const initialState: InteractionState = {
  currentFormData: initialFormState,
  interactionList: [],
  activeInteractionId: null,
  status: 'idle',
  error: null,
};

export const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    setFormData: (state, action: PayloadAction<FormStateDTO>) => {
      state.currentFormData = { ...state.currentFormData, ...action.payload };
    },
    resetForm: (state) => {
      state.currentFormData = initialFormState;
      state.activeInteractionId = null;
    },
    updateFormField: (state, action: PayloadAction<{ field: keyof FormStateDTO; value: any }>) => {
      state.currentFormData = {
        ...state.currentFormData,
        [action.payload.field]: action.payload.value
      };
    },
    setInteractionList: (state, action: PayloadAction<any[]>) => {
      state.interactionList = action.payload;
    },
    setActiveInteractionId: (state, action: PayloadAction<number | null>) => {
      state.activeInteractionId = action.payload;
    }
  },
});

export const {
  setFormData,
  resetForm,
  updateFormField,
  setInteractionList,
  setActiveInteractionId
} = interactionSlice.actions;

export default interactionSlice.reducer;
