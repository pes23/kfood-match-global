import type { Metadata } from "next";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "K-Food Match",
  description: "외국 음식을 기반으로 한국 음식을 추천하는 서비스",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
