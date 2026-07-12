import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface HCPProfile {
  id: number;
  name: string;
  specialty: string;
  hospital: string;
  contact_email?: string;
  phone?: string;
  city?: string;
}

interface HCPState {
  hcpList: HCPProfile[];
  selectedHcp: HCPProfile | null;
  historyData: any | null;
  loadingHistory: boolean;
}

const initialState: HCPState = {
  hcpList: [],
  selectedHcp: null,
  historyData: null,
  loadingHistory: false,
};

export const hcpSlice = createSlice({
  name: 'hcp',
  initialState,
  reducers: {
    setHcpList: (state, action: PayloadAction<HCPProfile[]>) => {
      state.hcpList = action.payload;
    },
    setSelectedHcp: (state, action: PayloadAction<HCPProfile | null>) => {
      state.selectedHcp = action.payload;
    },
    setHistoryData: (state, action: PayloadAction<any>) => {
      state.historyData = action.payload;
    },
    setLoadingHistory: (state, action: PayloadAction<boolean>) => {
      state.loadingHistory = action.payload;
    }
  },
});

export const { setHcpList, setSelectedHcp, setHistoryData, setLoadingHistory } = hcpSlice.actions;
export default hcpSlice.reducer;
