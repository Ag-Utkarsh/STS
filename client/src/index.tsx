import {
  PipecatAppBase,
  ErrorCard,
  SpinLoader,
  FullScreenContainer,
  Card,
  CardContent,
  Divider,
  UserAudioControl,
  ConnectButton,
  VoiceVisualizer,
  TranscriptOverlay,
  ThemeProvider,
  type PipecatBaseChildProps,
} from "@pipecat-ai/voice-ui-kit";

import { createRoot } from 'react-dom/client';


createRoot(document.getElementById('root')!).render(

  <ThemeProvider>
    <FullScreenContainer>
      <PipecatAppBase
        connectParams={{
          webrtcUrl: "/api/offer",
        }}
        transportType="smallwebrtc"
      >
        {({ client, handleConnect, handleDisconnect, error }: PipecatBaseChildProps) =>
          !client ? (
            <SpinLoader />
          ) : error ? (
            <ErrorCard>{error}</ErrorCard>
          ) : (
            <>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Bot Speech</h4>
                  <TranscriptOverlay participant="remote" />
                </div>
                <div>
                  <h4 className="text-sm font-medium mb-2">User Speech</h4>
                  <TranscriptOverlay participant="local" />
                </div>
              </div>
              <Card
                size="lg"
                shadow="xlong"
                noGradientBorder={false}
                rounded="xl"
              >
                <CardContent className="flex flex-col gap-4">
                  <VoiceVisualizer
                    participantType="bot"
                    className="bg-accent rounded-lg"
                  />
                  <Divider />
                  <div className="flex flex-col gap-4">
                    <UserAudioControl size="lg" />
                    <ConnectButton
                      size="lg"
                      onConnect={handleConnect}
                      onDisconnect={handleDisconnect}
                    />
                  </div>
                </CardContent>
              </Card>
            </>
          )
        }
      </PipecatAppBase>
    </FullScreenContainer>
  </ThemeProvider>
)