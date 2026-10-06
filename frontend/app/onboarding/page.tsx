"use client";

import React, { useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { usersService } from "@/lib/services/users";
import { wellnessService } from "@/lib/services/wellness";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Leaf, ArrowRight, ArrowLeft, Check } from "lucide-react";
import aarogyaLogo from "@/assets/aarogyalogo.png";

interface OnboardingData {
  dob: string;
  gender: string;
  height_cm: string;
  weight_kg: string;
  nationality: string;
  region: string;
  dietary_preferences: string[];
  commonly_eaten_foods: string;
  activity_level: string;
  wellness_goals: string[];
}

const STEPS = [
  { id: "welcome", title: "Welcome to Aarogya" },
  { id: "dob", title: "When were you born?" },
  { id: "body", title: "Your body details" },
  { id: "location", title: "Where are you from?" },
  { id: "diet", title: "Your dietary preferences" },
  { id: "activity", title: "Your activity level" },
  { id: "goals", title: "Your wellness goals" },
  { id: "done", title: "All set!" },
];

const DIETARY_OPTIONS = [
  "Vegetarian", "Vegan", "Gluten-free", "Dairy-free",
  "Keto", "Paleo", "Halal", "Kosher", "No restrictions",
];

const ACTIVITY_OPTIONS = [
  { value: "sedentary", label: "Sedentary", desc: "Little or no exercise" },
  { value: "light", label: "Lightly active", desc: "1–3 days/week" },
  { value: "moderate", label: "Moderately active", desc: "3–5 days/week" },
  { value: "active", label: "Very active", desc: "6–7 days/week" },
  { value: "extra", label: "Extra active", desc: "Physical job + exercise" },
];

const GOAL_OPTIONS = [
  "Lose weight", "Build muscle", "Improve fitness",
  "Eat healthier", "Sleep better", "Reduce stress",
  "Build consistency", "Track progress",
];

export default function OnboardingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState<OnboardingData>({
    dob: "",
    gender: "",
    height_cm: "",
    weight_kg: "",
    nationality: "",
    region: "",
    dietary_preferences: [],
    commonly_eaten_foods: "",
    activity_level: "",
    wellness_goals: [],
  });

  const totalSteps = STEPS.length;
  const progress = ((step + 1) / totalSteps) * 100;

  const toggleArrayItem = (arr: string[], item: string): string[] =>
    arr.includes(item) ? arr.filter((i) => i !== item) : [...arr, item];

  const handleNext = () => {
    if (step < STEPS.length - 1) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const handleSkip = () => {
    if (step < STEPS.length - 1) setStep(step + 1);
  };

  const handleFinish = async () => {
    setSaving(true);
    try {
      const profileUpdate: Record<string, unknown> = {};
      if (data.dob) profileUpdate.dob = data.dob;
      if (data.gender) profileUpdate.gender = data.gender;
      if (data.height_cm) profileUpdate.height_cm = parseFloat(data.height_cm);
      if (data.weight_kg) profileUpdate.weight_kg = parseFloat(data.weight_kg);
      if (data.nationality) profileUpdate.nationality = data.nationality;
      if (data.region) profileUpdate.region = data.region;
      if (data.dietary_preferences.length > 0) profileUpdate.dietary_preferences = data.dietary_preferences;
      if (data.commonly_eaten_foods) {
        profileUpdate.commonly_eaten_foods = data.commonly_eaten_foods.split(",").map((s) => s.trim()).filter(Boolean);
      }
      if (data.activity_level) profileUpdate.activity_level = data.activity_level;

      await usersService.updateProfile(profileUpdate as Parameters<typeof usersService.updateProfile>[0]);

      // Create wellness goals
      for (const goalTitle of data.wellness_goals) {
        await wellnessService.createGoal({ title: goalTitle, category: "general" });
      }

      router.push("/today");
    } catch {
      // Still navigate on error
      router.push("/today");
    } finally {
      setSaving(false);
    }
  };

  const renderStep = () => {
    switch (STEPS[step].id) {
      case "welcome":
        return (
          <div className="flex flex-col gap-6">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center">
              <Leaf className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-white mb-2">
                Hello{user?.name ? `, ${user.name}` : ""}! 👋
              </h2>
              <p className="text-white/60 leading-relaxed">
                Let&apos;s get to know you so Aaryu can give you truly personalized wellness guidance.
                <br /><br />
                This will take about 2 minutes and you can update everything later in your profile.
              </p>
            </div>
          </div>
        );

      case "dob":
        return (
          <div className="flex flex-col gap-5">
            <p className="text-white/60 text-sm">This helps us provide age-appropriate recommendations.</p>
            <div className="flex flex-col gap-2">
              <label className="text-white/70 text-xs font-medium uppercase tracking-wide">Date of birth</label>
              <Input
                type="date"
                value={data.dob}
                onChange={(e) => setData({ ...data, dob: e.target.value })}
                className="bg-black/30 border-white/10 text-white focus-visible:border-primary focus-visible:ring-primary/20"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-white/70 text-xs font-medium uppercase tracking-wide">Gender (optional)</label>
              <div className="grid grid-cols-3 gap-2">
                {["Male", "Female", "Other"].map((g) => (
                  <button
                    key={g}
                    onClick={() => setData({ ...data, gender: data.gender === g ? "" : g })}
                    className={`rounded-lg border px-3 py-2.5 text-sm transition-all duration-150 ${
                      data.gender === g
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-white/10 text-white/60 hover:border-white/20 hover:text-white"
                    }`}
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>
          </div>
        );

      case "body":
        return (
          <div className="flex flex-col gap-5">
            <p className="text-white/60 text-sm">Used for personalized activity and nutrition guidance.</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-2">
                <label className="text-white/70 text-xs font-medium uppercase tracking-wide">Height (cm)</label>
                <Input
                  type="number"
                  placeholder="170"
                  value={data.height_cm}
                  onChange={(e) => setData({ ...data, height_cm: e.target.value })}
                  min={50}
                  max={250}
                  className="bg-black/30 border-white/10 text-white placeholder:text-white/30 focus-visible:border-primary focus-visible:ring-primary/20"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-white/70 text-xs font-medium uppercase tracking-wide">Weight (kg)</label>
                <Input
                  type="number"
                  placeholder="70"
                  value={data.weight_kg}
                  onChange={(e) => setData({ ...data, weight_kg: e.target.value })}
                  min={20}
                  max={300}
                  className="bg-black/30 border-white/10 text-white placeholder:text-white/30 focus-visible:border-primary focus-visible:ring-primary/20"
                />
              </div>
            </div>
          </div>
        );

      case "location":
        return (
          <div className="flex flex-col gap-5">
            <p className="text-white/60 text-sm">Used for cultural, dietary, and regional context only.</p>
            <div className="flex flex-col gap-2">
              <label className="text-white/70 text-xs font-medium uppercase tracking-wide">Nationality</label>
              <Input
                type="text"
                placeholder="e.g. Indian, American, British"
                value={data.nationality}
                onChange={(e) => setData({ ...data, nationality: e.target.value })}
                className="bg-black/30 border-white/10 text-white placeholder:text-white/30 focus-visible:border-primary focus-visible:ring-primary/20"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-white/70 text-xs font-medium uppercase tracking-wide">Region / City</label>
              <Input
                type="text"
                placeholder="e.g. South India, New York, London"
                value={data.region}
                onChange={(e) => setData({ ...data, region: e.target.value })}
                className="bg-black/30 border-white/10 text-white placeholder:text-white/30 focus-visible:border-primary focus-visible:ring-primary/20"
              />
            </div>
          </div>
        );

      case "diet":
        return (
          <div className="flex flex-col gap-5">
            <div>
              <p className="text-white/60 text-sm mb-3">Select all that apply.</p>
              <div className="flex flex-wrap gap-2">
                {DIETARY_OPTIONS.map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setData({ ...data, dietary_preferences: toggleArrayItem(data.dietary_preferences, opt) })}
                    className={`rounded-full border px-3.5 py-1.5 text-sm transition-all duration-150 ${
                      data.dietary_preferences.includes(opt)
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-white/10 text-white/60 hover:border-white/20 hover:text-white"
                    }`}
                  >
                    {data.dietary_preferences.includes(opt) && (
                      <span className="mr-1">✓</span>
                    )}
                    {opt}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-white/70 text-xs font-medium uppercase tracking-wide">
                Foods you commonly eat
              </label>
              <Input
                type="text"
                placeholder="e.g. rice, dal, chicken, salads"
                value={data.commonly_eaten_foods}
                onChange={(e) => setData({ ...data, commonly_eaten_foods: e.target.value })}
                className="bg-black/30 border-white/10 text-white placeholder:text-white/30 focus-visible:border-primary focus-visible:ring-primary/20"
              />
              <p className="text-white/30 text-xs">Separate with commas</p>
            </div>
          </div>
        );

      case "activity":
        return (
          <div className="flex flex-col gap-3">
            <p className="text-white/60 text-sm mb-1">How active are you generally?</p>
            {ACTIVITY_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setData({ ...data, activity_level: data.activity_level === opt.value ? "" : opt.value })}
                className={`rounded-xl border px-4 py-3 text-left transition-all duration-150 ${
                  data.activity_level === opt.value
                    ? "border-primary bg-primary/10"
                    : "border-white/10 hover:border-white/20"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className={`font-medium text-sm ${data.activity_level === opt.value ? "text-primary" : "text-white"}`}>
                      {opt.label}
                    </div>
                    <div className="text-white/40 text-xs mt-0.5">{opt.desc}</div>
                  </div>
                  {data.activity_level === opt.value && (
                    <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        );

      case "goals":
        return (
          <div className="flex flex-col gap-4">
            <p className="text-white/60 text-sm">Select what you want to focus on.</p>
            <div className="flex flex-wrap gap-2">
              {GOAL_OPTIONS.map((goal) => (
                <button
                  key={goal}
                  onClick={() => setData({ ...data, wellness_goals: toggleArrayItem(data.wellness_goals, goal) })}
                  className={`rounded-full border px-3.5 py-1.5 text-sm transition-all duration-150 ${
                    data.wellness_goals.includes(goal)
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-white/10 text-white/60 hover:border-white/20 hover:text-white"
                  }`}
                >
                  {data.wellness_goals.includes(goal) && <span className="mr-1">✓</span>}
                  {goal}
                </button>
              ))}
            </div>
          </div>
        );

      case "done":
        return (
          <div className="flex flex-col gap-6">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center">
              <Check className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-white mb-2">You&apos;re all set!</h2>
              <p className="text-white/60 leading-relaxed">
                Aaryu now has a good understanding of you. Your experience will become more
                personalized as you interact with the app.
                <br /><br />
                You can always update your profile settings later.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const isLastStep = step === STEPS.length - 1;
  const isFirstStep = step === 0;

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-6">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="flex items-center gap-3 mb-10">
          <Image src={aarogyaLogo} alt="" width={56} height={56} className="h-12 w-12 rounded-full object-contain" />
          <span className="text-white font-semibold tracking-tight">Aarogya</span>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-white/40 text-xs">
              Step {step + 1} of {totalSteps}
            </span>
            <span className="text-primary text-xs font-medium">{STEPS[step].title}</span>
          </div>
          <div className="h-1 bg-white/8 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Step content */}
        <div key={step} className="slide-up bg-[#1E2126] rounded-2xl p-6 mb-6">
          {STEPS[step].id !== "welcome" && STEPS[step].id !== "done" && (
            <h2 className="text-lg font-semibold text-white mb-4">{STEPS[step].title}</h2>
          )}
          {renderStep()}
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-3">
          {!isFirstStep && (
            <Button
              variant="outline"
              onClick={handleBack}
              className="border-white/10 text-white/60 hover:text-white hover:border-white/20 bg-transparent"
              disabled={saving}
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back
            </Button>
          )}

          <div className="flex-1" />

          {!isLastStep && step > 0 && (
            <Button
              variant="ghost"
              onClick={handleSkip}
              className="text-white/40 hover:text-white/60"
              disabled={saving}
            >
              Skip
            </Button>
          )}

          {isLastStep ? (
            <Button
              onClick={handleFinish}
              disabled={saving}
              className="bg-primary hover:bg-primary/90 text-white min-w-[120px]"
            >
              {saving ? <Spinner className="w-4 h-4" /> : (
                <span className="flex items-center gap-2">
                  Start <ArrowRight className="w-4 h-4" />
                </span>
              )}
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              className="bg-primary hover:bg-primary/90 text-white"
            >
              Continue
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
