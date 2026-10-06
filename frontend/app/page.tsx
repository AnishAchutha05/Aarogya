"use client";

import { useEffect } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { Spinner } from "@/components/ui/spinner";
import aarogyaLogo from "@/assets/aarogyalogo.png";

export default function RootPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.replace("/today");
      } else {
        router.replace("/login");
      }
    }
  }, [user, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="flex items-center gap-3">
          <Image src={aarogyaLogo} alt="" width={64} height={64} className="h-14 w-14 rounded-full object-contain" />
          <span className="text-lg font-semibold tracking-tight text-foreground">Aarogya</span>
        </div>
        <Spinner className="text-primary" />
      </div>
    </div>
  );
}
