import Image from "next/image";

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-background py-12 mt-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-start gap-12 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Image
                src="/logo_horizontal.png"
                alt="Lotara"
                width={100}
                height={32}
                className="h-8 w-auto"
              />
            </div>
            <p className="text-sm text-muted-foreground max-w-xs">
              AI-powered travel planning personalized to your unique style
            </p>
          </div>

          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-foreground text-sm">Product</h3>
            <a
              href="#"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              How it works
            </a>
            <a
              href="#"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Pricing
            </a>
          </div>

          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-foreground text-sm">Company</h3>
            <a
              href="#"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              About
            </a>
            <a
              href="#"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Contact
            </a>
          </div>
        </div>

        <div className="border-t border-border/40 pt-8 text-center text-xs text-muted-foreground">
          <p>© 2026 Lotara. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
