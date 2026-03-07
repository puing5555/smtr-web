import type { Metadata } from "next";
import "./globals.css";
import MainLayout from "@/components/MainLayout";

export const metadata: Metadata = {
  title: "투자SNS",
  description: "투자 소셜 네트워크 서비스",
};

// GitHub Pages SPA 404 redirect 핸들러
const spaRedirectScript = `
(function() {
  var redirect = sessionStorage.getItem('redirect');
  if (redirect) {
    sessionStorage.removeItem('redirect');
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, '', '/invest-sns' + redirect);
    }
  }
})();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <script dangerouslySetInnerHTML={{ __html: spaRedirectScript }} />
      </head>
      <body className="bg-[#f4f4f4] text-[#191f28]">
        <MainLayout>{children}</MainLayout>
      </body>
    </html>
  );
}