import './App.css';
import Banner from './modules/Banner/Banner';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { appTheme } from './themes/theme.ts';
import { WebSocketListener } from './modules/WebSocket/WebSocketListener';
import ViewerWindowConnected from './modules/ViewerPanel/ViewerWindow';

function App() {

  return (
    <ThemeProvider theme={appTheme}>
      <CssBaseline enableColorScheme/>
      <div className="App">
      <WebSocketListener />
      {/* <Banner /> */}
      <header className="App-body">
        <ViewerWindowConnected />
      </header>
      </div>
    </ThemeProvider>
  );
}

export default App;
