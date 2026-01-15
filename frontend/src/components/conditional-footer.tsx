"use client";

import { usePathname } from "next/navigation";
import { Footer } from "./footer";

const PAGES_WITHOUT_FOOTER = ["/onboarding", "/admin", "/explain"];

export function ConditionalFooter() {
  const pathname = usePathname();

  if (PAGES_WITHOUT_FOOTER.includes(pathname)) {
    return null;
  }

  return <Footer />;
}
