import { AnimationPanel } from './modules/AnimationPanel/AnimationPanel';
// TODO: determine whether we need a banner
// import Banner from './modules/Banner/Banner';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { appTheme } from './themes/theme.ts';
// TODO: enable vertex streaming via websocket
// import { WebSocketListener } from './modules/WebSocket/WebSocketListener';
import ViewerWindowConnected from './modules/ViewerPanel/ViewerWindow';
import { SidePanel } from './modules/SidePanel/SidePanel';

function App() {

  return (
    <ThemeProvider theme={appTheme}>
      <CssBaseline enableColorScheme/>
      <div className="App">
      {/* TODO: enable vertex streaming via websocket*/}
      {/* <WebSocketListener /> */}
      {/* TODO: determine whether we need a banner*/}
      {/* <Banner /> */}
      <header className="App-body">
        <ViewerWindowConnected />
        <SidePanel/>
        <AnimationPanel/>
      </header>
      </div>
    </ThemeProvider>
  );
}

export default App;
