"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { authService } from "@/lib/services/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CommunityTweetCard } from "@/components/ui/community-tweet-card";
import aarogyaLogo from "@/assets/aarogyalogo.png";
import googleLogo from "@/assets/googlelogo.png";
import yahooLogo from "@/assets/yahoologo.png";
import greeneryBackground from "@/assets/greenery.avif";
import riversideRunner from "@/assets/Pasted image.png";
import blueRunner from "@/assets/Pasted image (2).png";
import healthyFood from "@/assets/Pasted image (3).png";
import mindfulPause from "@/assets/Pasted image (4).png";
import familyWellness from "@/assets/Pasted image (5).png";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  type CarouselApi,
} from "@/components/ui/carousel";
import { Eye, EyeOff } from "lucide-react";

type Mode = "login" | "register";

const testimonials = [
  {
    quote: "Aarogya helped me build consistent habits without feeling overwhelmed. Aaryu actually understands my schedule.",
    author: "Priya S.",
    handle: "@priya_s",
    initials: "PS",
    image: riversideRunner,
    imageAlt: "Runner following a riverside path",
  },
  {
    quote: "Finally a wellness app that adapts to me. When I'm tired, it gives me shorter workouts. Simple.",
    author: "Marcus T.",
    handle: "@marcus_t",
    initials: "MT",
    image: blueRunner,
    imageAlt: "Runner enjoying an outdoor workout",
  },
  {
    quote: "The roadmap feature changed how I think about my goals. It's like having a personal wellness strategist.",
    author: "Ananya R.",
    handle: "@ananya_r",
    initials: "AR",
    image: familyWellness,
    imageAlt: "Family sharing a happy moment at home",
  },
  {
    quote: "I love how Aaryu remembers context from our previous conversations. It feels genuinely personal.",
    author: "David K.",
    handle: "@david_k",
    initials: "DK",
    image: mindfulPause,
    imageAlt: "A person taking a quiet moment to meditate outdoors",
  },
  {
    quote: "Wellness works best when it fits around the people and moments that matter to you.",
    author: "Aarogya",
    handle: "@aarogya",
    initials: "A",
    image: healthyFood,
    imageAlt: "A colorful selection of nourishing foods",
    isBrandNote: true,
  },
];

const carouselTestimonials = [...testimonials, ...testimonials];

export default function LoginPage() {
  const { user, loading: authLoading, login, register } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTestimonial, setActiveTestimonial] = useState(0);
  const [testimonialCarousel, setTestimonialCarousel] = useState<CarouselApi>();

  useEffect(() => {
    if (!authLoading && user) {
      router.replace("/today");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (!testimonialCarousel) return;

    const updateActiveTestimonial = () => {
      setActiveTestimonial(testimonialCarousel.selectedScrollSnap() % testimonials.length);
    };
    const normalizeRepeatedTrack = () => {
      const selectedIndex = testimonialCarousel.selectedScrollSnap();
      if (selectedIndex >= testimonials.length) {
        testimonialCarousel.scrollTo(selectedIndex - testimonials.length, true);
      }
    };

    testimonialCarousel.on("select", updateActiveTestimonial);
    testimonialCarousel.on("settle", normalizeRepeatedTrack);
    const interval = setInterval(() => testimonialCarousel.scrollNext(), 5000);

    return () => {
      clearInterval(interval);
      testimonialCarousel.off("select", updateActiveTestimonial);
      testimonialCarousel.off("settle", normalizeRepeatedTrack);
    };
  }, [testimonialCarousel]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
        router.push("/today");
      } else {
        await register(email, password, name);
        router.push("/onboarding");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Spinner className="text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black flex">
      {/* Left — Testimonial panel (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-[55%] flex-col justify-between p-12 relative overflow-hidden">
        <Image
          src={greeneryBackground}
          alt=""
          fill
          sizes="55vw"
          priority
          className="object-cover object-center"
        />
        <div className="absolute inset-0 bg-black/55" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/25 via-transparent to-black/55" />

        {/* Logo */}
        <div className="relative flex items-center gap-3">
          <Image
            src={aarogyaLogo}
            alt="Aarogya"
            width={72}
            height={72}
            className="h-16 w-16 rounded-full object-contain"
            priority
          />
          <span className="text-lg font-semibold tracking-tight text-white">Aarogya</span>
        </div>

        {/* Testimonial */}
        <div className="relative flex flex-col gap-6">
          <div className="w-12 h-0.5 bg-primary" />
          <Carousel
            setApi={setTestimonialCarousel}
            opts={{ loop: false, align: "start", containScroll: false, duration: 35 }}
            className="w-full max-w-[570px]"
          >
            <CarouselContent>
              {carouselTestimonials.map((testimonial, index) => (
                <CarouselItem key={`${testimonial.initials}-${index}`}>
                  <CommunityTweetCard
                    author={testimonial.author}
                    handle={testimonial.handle}
                    initials={testimonial.initials}
                    text={testimonial.quote}
                    image={testimonial.image}
                    imageAlt={testimonial.imageAlt}
                    isBrandNote={testimonial.isBrandNote}
                    priority={index === 0}
                  />
                </CarouselItem>
              ))}
            </CarouselContent>
          </Carousel>

          {/* Carousel position indicators */}
          <div className="flex gap-2 mt-2" role="group" aria-label="Choose a testimonial">
            {testimonials.map((testimonial, i) => (
              <button
                key={testimonial.initials}
                type="button"
                onClick={() => testimonialCarousel?.scrollTo(i)}
                className="transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-full"
                aria-label={`Show testimonial ${i + 1}`}
                aria-current={i === activeTestimonial ? "true" : undefined}
              >
                <span
                  className="block h-1 rounded-full transition-all duration-300"
                  style={{
                    width: i === activeTestimonial ? "24px" : "8px",
                    backgroundColor: i === activeTestimonial ? "#0B6623" : "rgba(255,255,255,0.2)",
                  }}
                />
              </button>
            ))}
          </div>
        </div>

        {/* Bottom tagline */}
        <div className="relative">
          <p className="text-white/30 text-sm">
            Your personal wellness companion.
          </p>
        </div>
      </div>

      {/* Right — Auth form */}
      <div className="w-full lg:w-[45%] flex items-center justify-center p-6 bg-[#1E2126]">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <Image
              src={aarogyaLogo}
              alt="Aarogya"
              width={56}
              height={56}
              className="h-12 w-12 rounded-full object-contain"
              priority
            />
            <span className="text-base font-semibold tracking-tight text-white">Aarogya</span>
          </div>

          <Card className="gap-0 border-white/10 bg-[#17191d] py-0 text-white shadow-xl shadow-black/20">
            <CardHeader className="grid-cols-[1fr_auto] items-center gap-4 border-b border-white/10 px-5 py-5 sm:px-6">
              <div className="space-y-1">
                <CardTitle className="text-lg font-semibold text-white">
                  {mode === "login" ? "Login to your account" : "Create your account"}
                </CardTitle>
                <CardDescription className="text-sm text-white/55">
                  {mode === "login"
                    ? "Enter your email below to log in to your account."
                    : "Start personalizing your wellness with Aarogya."}
                </CardDescription>
              </div>
              <button
                type="button"
                onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}
                className="rounded-md px-2 py-1.5 text-sm font-medium text-white/85 transition-colors hover:bg-white/5 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              >
                {mode === "login" ? "Sign Up" : "Sign In"}
              </button>
            </CardHeader>

            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-4 px-5 py-5 sm:px-6">
                {mode === "register" && (
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-white/90" htmlFor="name">Name</label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="Your name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      className="h-10 border-white/10 bg-[#202226] text-white placeholder:text-white/35 focus-visible:border-primary focus-visible:ring-primary/25"
                      autoComplete="name"
                    />
                  </div>
                )}

                <div className="flex flex-col gap-1.5">
                  <label className="text-sm font-medium text-white/90" htmlFor="email">Email</label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="h-10 border-white/10 bg-[#202226] text-white placeholder:text-white/35 focus-visible:border-primary focus-visible:ring-primary/25"
                    autoComplete="email"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-white/90" htmlFor="password">Password</label>
                  </div>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      minLength={8}
                      className="h-10 border-white/10 bg-[#202226] pr-10 text-white placeholder:text-white/35 focus-visible:border-primary focus-visible:ring-primary/25"
                      autoComplete={mode === "login" ? "current-password" : "new-password"}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-white/45 transition-colors hover:text-white/80"
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="rounded-lg border border-red-400/20 bg-red-400/10 px-3 py-2">
                    <p className="text-sm text-red-300">{error}</p>
                  </div>
                )}
              </CardContent>

              <CardFooter className="flex-col items-stretch gap-2 border-t border-white/10 bg-white/[0.025] px-5 py-4 sm:px-6">
                <Button
                  type="submit"
                  disabled={loading}
                  className="h-10 w-full bg-primary font-medium text-white hover:bg-primary/90"
                >
                  {loading ? <Spinner className="h-4 w-4 text-white" /> : mode === "login" ? "Login" : "Create account"}
                </Button>

                <div className="flex items-center gap-3 py-1">
                  <span className="h-px flex-1 bg-white/10" />
                  <span className="text-xs text-white/45">or continue with</span>
                  <span className="h-px flex-1 bg-white/10" />
                </div>

                <Button
                  type="button"
                  variant="outline"
                  className="h-10 w-full justify-center gap-4 border-white/10 bg-[#202226] text-white hover:bg-white/10"
                  onClick={() => { setError(""); window.location.assign(authService.getGoogleLoginUrl()); }}
                >
                  <Image src={googleLogo} alt="" width={20} height={20} />
                  <span>Continue with Google</span>
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="h-10 w-full justify-center gap-4 border-white/10 bg-[#202226] text-white hover:bg-white/10"
                  onClick={() => { setError(""); window.location.assign(authService.getYahooLoginUrl()); }}
                >
                  <Image src={yahooLogo} alt="" width={20} height={20} />
                  <span>Continue with Yahoo</span>
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}
