import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "InsightRural | Premium Admission Counselor",
  description: "AI-powered college admission prediction and counseling platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-black text-white selection:bg-indigo-500/30`}>
        {/* Ambient Background Glows */}
        <div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-900/20 blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] rounded-full bg-purple-900/20 blur-[100px]" />
        </div>
        
        {children}
      </body>
    </html>
  );
}
