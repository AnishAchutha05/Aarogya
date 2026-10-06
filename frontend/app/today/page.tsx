"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/contexts/auth-context";
import { ProtectedLayout } from "@/components/layout/protected-layout";
import { wellnessService } from "@/lib/services/wellness";
import { plansService } from "@/lib/services/plans";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { Separator } from "@/components/ui/separator";
import type { GoalResponse, ActivityResponse, CheckInResponse, InsightResponse, PlanResponse } from "@/types";
import {
  Zap, Sun, Moon, Activity, Target, ChevronRight, Check,
  MessageCircle, Flame, Droplets, Clock, Plus
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
};

const getDateString = () => {
  return new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
};

const ENERGY_OPTIONS = [
  { label: "Energized", icon: Zap, score: 5, color: "#0B6623" },
  { label: "Good", icon: Sun, score: 4, color: "#4ade80" },
  { label: "Okay", icon: Activity, score: 3, color: "#FFCE1B" },
  { label: "Tired", icon: Moon, score: 2, color: "#f97316" },
  { label: "Exhausted", icon: Moon, score: 1, color: "#ef4444" },
];

export default function TodayPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [checkingIn, setCheckingIn] = useState(false);
  const [selectedEnergy, setSelectedEnergy] = useState<number | null>(null);
  const [todayPlan, setTodayPlan] = useState<PlanResponse | null>(null);
  const [goals, setGoals] = useState<GoalResponse[]>([]);
  const [insights, setInsights] = useState<InsightResponse[]>([]);
  const [todayCheckin, setTodayCheckin] = useState<CheckInResponse | null>(null);
  const [completingItem, setCompletingItem] = useState<string | null>(null);
  const [localPlan, setLocalPlan] = useState<PlanResponse | null>(null);

  const today = new Date().toISOString().split("T")[0];
  const dayOfWeek = new Date().getDay(); // 0=Sun, 1=Mon...

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [goalsData, plans, insightsData, checkins] = await Promise.allSettled([
        wellnessService.listGoals(),
        plansService.listPlans(),
        wellnessService.getInsights(),
        wellnessService.getRecentCheckins(1),
      ]);

      if (goalsData.status === "fulfilled") setGoals(goalsData.value);
      if (insightsData.status === "fulfilled") setInsights(insightsData.value.slice(0, 3));
      if (checkins.status === "fulfilled" && checkins.value.length > 0) {
        const tc = checkins.value.find((c) => c.check_in_date === today);
        setTodayCheckin(tc || null);
        if (tc) setSelectedEnergy(tc.energy_score ?? null);
      }
      if (plans.status === "fulfilled") {
        const activePlan = plans.value.find((p) => p.is_active);
        setTodayPlan(activePlan || null);
        setLocalPlan(activePlan || null);
      }
    } finally {
      setLoading(false);
    }
  }, [today]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCheckIn = async (score: number) => {
    setSelectedEnergy(score);
    setCheckingIn(true);
    try {
      const result = await wellnessService.checkIn({
        check_in_date: today,
        energy_score: score,
      });
      setTodayCheckin(result);
    } catch {
      // Still show selected state
    } finally {
      setCheckingIn(false);
    }
  };

  const handleCompleteItem = async (planId: string, itemId: string) => {
    setCompletingItem(itemId);
    try {
      const updated = await plansService.completePlanItem(planId, itemId);
      setLocalPlan((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          items: prev.items.map((item) =>
            item.id === itemId ? { ...item, is_completed: true, completed_at: today } : item
          ),
        };
      });
    } catch {}
    finally {
      setCompletingItem(null);
    }
  };

  const todayItems = localPlan?.items.filter(
    (item) => item.day_of_week === undefined || item.day_of_week === dayOfWeek || item.day_of_week === null
  ) ?? [];

  const completedCount = todayItems.filter((i) => i.is_completed).length;
  const totalCount = todayItems.length;
  const progressPct = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  if (loading) {
    return (
      <ProtectedLayout>
        <div className="p-6 max-w-2xl mx-auto space-y-6">
          <div className="space-y-2">
            <Skeleton className="h-6 w-32 rounded" />
            <Skeleton className="h-4 w-48 rounded" />
          </div>
          <div className="grid gap-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-20 w-full rounded-xl" />
            ))}
          </div>
        </div>
      </ProtectedLayout>
    );
  }

  return (
    <ProtectedLayout>
      <div className="p-6 max-w-2xl mx-auto space-y-6 page-enter">
        {/* Greeting */}
        <div>
          <h1 className="text-2xl font-semibold text-foreground">
            {getGreeting()}{user?.name ? `, ${user.name.split(" ")[0]}` : ""}
          </h1>
          <p className="text-muted-foreground text-sm mt-0.5">{getDateString()}</p>
        </div>

        {/* Check-in card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              How are you feeling today?
            </CardTitle>
          </CardHeader>
          <CardContent>
            {checkingIn ? (
              <div className="flex items-center gap-2 text-muted-foreground text-sm py-2">
                <Spinner className="w-4 h-4" />
                <span>Saving check-in...</span>
              </div>
            ) : todayCheckin && selectedEnergy ? (
              <div className="flex items-center gap-3">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: ENERGY_OPTIONS.find((e) => e.score === selectedEnergy)?.color + "20" }}
                >
                  <Zap
                    className="w-4 h-4"
                    style={{ color: ENERGY_OPTIONS.find((e) => e.score === selectedEnergy)?.color }}
                  />
                </div>
                <div>
                  <div className="text-sm font-medium text-foreground">
                    {ENERGY_OPTIONS.find((e) => e.score === selectedEnergy)?.label}
                  </div>
                  <div className="text-xs text-muted-foreground">Check-in recorded</div>
                </div>
                <button
                  onClick={() => { setTodayCheckin(null); setSelectedEnergy(null); }}
                  className="ml-auto text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  Change
                </button>
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {ENERGY_OPTIONS.map((opt) => {
                  const Icon = opt.icon;
                  return (
                    <button
                      key={opt.label}
                      onClick={() => handleCheckIn(opt.score)}
                      className={`flex items-center gap-1.5 px-3 py-2 rounded-lg border text-sm transition-all duration-150 ${
                        selectedEnergy === opt.score
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border text-muted-foreground hover:border-foreground/20 hover:text-foreground"
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Today's Plan */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Today&apos;s Plan
              </h2>
              {totalCount > 0 && (
                <p className="text-xs text-muted-foreground mt-0.5">
                  {completedCount} of {totalCount} completed
                </p>
              )}
            </div>
            {todayPlan && totalCount > 0 && (
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500"
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
                <span className="text-xs text-muted-foreground">{Math.round(progressPct)}%</span>
              </div>
            )}
          </div>

          {!todayPlan || todayItems.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center">
                <div className="w-10 h-10 rounded-xl bg-muted flex items-center justify-center mx-auto mb-3">
                  <Activity className="w-5 h-5 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground mb-1">No activities for today</p>
                <p className="text-xs text-muted-foreground/70 mb-4">
                  Ask Aaryu to build you a plan or add activities manually.
                </p>
                <div className="flex gap-2 justify-center">
                  <Button size="sm" className="bg-primary text-white" onClick={() => router.push("/coach")}>
                    <MessageCircle className="w-3.5 h-3.5 mr-1.5" />
                    Ask Aaryu
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="flex flex-col gap-2.5">
              {todayItems.map((item) => (
                <Card
                  key={item.id}
                  className={`transition-all duration-200 ${item.is_completed ? "opacity-60" : ""}`}
                >
                  <CardContent className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => !item.is_completed && handleCompleteItem(localPlan!.id, item.id)}
                        disabled={item.is_completed || completingItem === item.id}
                        className={`w-7 h-7 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all duration-200 ${
                          item.is_completed
                            ? "border-primary bg-primary"
                            : "border-border hover:border-primary"
                        }`}
                        aria-label={item.is_completed ? "Completed" : "Mark as complete"}
                      >
                        {completingItem === item.id ? (
                          <Spinner className="w-3 h-3 text-primary" />
                        ) : item.is_completed ? (
                          <Check className="w-3.5 h-3.5 text-white" />
                        ) : null}
                      </button>
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium ${item.is_completed ? "line-through text-muted-foreground" : "text-foreground"}`}>
                          {item.title}
                        </div>
                        {item.description && (
                          <div className="text-xs text-muted-foreground truncate mt-0.5">{item.description}</div>
                        )}
                      </div>
                      {item.duration_minutes && (
                        <div className="flex items-center gap-1 text-xs text-muted-foreground flex-shrink-0">
                          <Clock className="w-3 h-3" />
                          {item.duration_minutes}m
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Goals section */}
        {goals.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Active Goals
              </h2>
              <Link href="/account" className="text-xs text-primary hover:text-primary/80 transition-colors">
                View all
              </Link>
            </div>
            <div className="flex flex-col gap-2">
              {goals.filter((g) => g.is_active && !g.is_completed).slice(0, 3).map((goal) => {
                const progress = goal.target_value && goal.current_value
                  ? Math.min((goal.current_value / goal.target_value) * 100, 100)
                  : null;
                return (
                  <Card key={goal.id} size="sm">
                    <CardContent className="py-3 px-4">
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2.5 min-w-0">
                          <Target className="w-4 h-4 text-primary flex-shrink-0" />
                          <div className="min-w-0">
                            <div className="text-sm font-medium text-foreground truncate">{goal.title}</div>
                            {goal.category && (
                              <div className="text-xs text-muted-foreground">{goal.category}</div>
                            )}
                          </div>
                        </div>
                        {progress !== null && (
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary rounded-full transition-all duration-500"
                                style={{ width: `${progress}%` }}
                              />
                            </div>
                            <span className="text-xs text-muted-foreground">{Math.round(progress)}%</span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* Insights */}
        {insights.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-3">
              Insights
            </h2>
            <div className="flex flex-col gap-2">
              {insights.map((insight) => (
                <Card key={insight.id} size="sm">
                  <CardContent className="py-3 px-4">
                    <div className="text-xs font-medium text-primary uppercase tracking-wide mb-1">
                      {insight.category || "Insight"}
                    </div>
                    <div className="text-sm text-foreground font-medium mb-0.5">{insight.title}</div>
                    <div className="text-xs text-muted-foreground line-clamp-2">{insight.content}</div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Quick actions */}
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-3">
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              onClick={() => router.push("/coach")}
              className="h-auto py-3 border-border hover:border-primary/30 hover:bg-primary/5 flex-col gap-1.5"
            >
              <MessageCircle className="w-4 h-4 text-primary" />
              <span className="text-xs">Chat with Aaryu</span>
            </Button>
            <Button
              variant="outline"
              onClick={() => router.push("/progress")}
              className="h-auto py-3 border-border hover:border-primary/30 hover:bg-primary/5 flex-col gap-1.5"
            >
              <TrendingUp className="w-4 h-4 text-primary" />
              <span className="text-xs">View Progress</span>
            </Button>
          </div>
        </div>
      </div>
    </ProtectedLayout>
  );
}

// Needed for TrendingUp import
function TrendingUp(props: React.ComponentProps<typeof Activity>) {
  return <Activity {...props} />;
}
