import { createTheme } from '@mui/material/styles';

export const appTheme = createTheme({
  palette: {
    primary: { main: '#EEEEEE' },
    secondary: { main: '#FFD369' },
    text: {
      primary: '#EEEEEE',
      secondary: '#FFD369',
      disabled: '#555555',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#222831',
        },
      },
    },
  },
});
