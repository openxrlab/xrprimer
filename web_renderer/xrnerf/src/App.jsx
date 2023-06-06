import './App.css';
// TODO: determine whether we need a banner
// import Banner from './modules/Banner/Banner';
import { SidePanel } from './modules/SidePanel/SidePanel';
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
      {/* TODO: determine whether we need a banner */}
      {/* <Banner /> */}
      <header className="App-body">
        <ViewerWindowConnected />
        <SidePanel />
      </header>
      </div>
    </ThemeProvider>
  );
}

export default App;
