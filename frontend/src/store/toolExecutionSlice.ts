import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { ToolBadgeDTO } from '../services/api';

interface ToolExecutionState {
  lastTool: ToolBadgeDTO | null;
  history: ToolBadgeDTO[];
  isRunning: boolean;
}

const initialState: ToolExecutionState = {
  lastTool: null,
  history: [],
  isRunning: false,
};

export const toolExecutionSlice = createSlice({
  name: 'toolExecution',
  initialState,
  reducers: {
    setToolRunning: (state, action: PayloadAction<boolean>) => {
      state.isRunning = action.payload;
    },
    recordToolExecution: (state, action: PayloadAction<ToolBadgeDTO>) => {
      state.lastTool = action.payload;
      state.history.unshift(action.payload);
      state.isRunning = false;
    },
    clearToolHistory: (state) => {
      state.lastTool = null;
      state.history = [];
    }
  },
});

export const { setToolRunning, recordToolExecution, clearToolHistory } = toolExecutionSlice.actions;
export default toolExecutionSlice.reducer;
