import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './chatSlice';
import interactionReducer from './interactionSlice';
import hcpReducer from './hcpSlice';
import toolExecutionReducer from './toolExecutionSlice';
import notificationReducer from './notificationSlice';

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    interaction: interactionReducer,
    hcp: hcpReducer,
    toolExecution: toolExecutionReducer,
    notification: notificationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
