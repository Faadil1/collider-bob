import React from "react";
import { Composition } from "remotion";
import { Film, TOTAL_FRAMES } from "./Film";
import { FPS } from "./timeline";

export const Root: React.FC = () => (
  <Composition id="Collider" component={Film} durationInFrames={TOTAL_FRAMES} fps={FPS} width={1920} height={1080} />
);
