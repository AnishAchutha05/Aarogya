"use client";

import React, { useState, useEffect } from "react";
import { ProtectedLayout } from "@/components/layout/protected-layout";
import { wellnessService } from "@/lib/services/wellness";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Activity, Zap, Droplets, Moon, Calendar, TrendingUp } from "lucide-react";
import type { ActivityLogResponse, CheckInResponse } from "@/types";

export default function ProgressPage() {
  const [loading, setLoading] = useState(true);
  const [activities, setActivities] = useState<ActivityLogResponse[]>([]);
  const [checkins, setCheckins] = useState<CheckInResponse[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [acts, chks] = await Promise.all([
          wellnessService.getActivityHistory(),
          wellnessService.getRecentCheckins(7)
        ]);
        setActivities(acts);
        setCheckins(chks);
      } catch {
        // error
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <ProtectedLayout title="Progress">
        <div className="flex h-[50vh] items-center justify-center">
          <Spinner className="text-primary" />
        </div>
      </ProtectedLayout>
    );
  }

  // Calculate some simple stats
  const totalDuration = activities.reduce((acc, curr) => acc + (curr.duration_minutes || 0), 0);
  const avgEnergy = checkins.length > 0 
    ? checkins.reduce((acc, curr) => acc + (curr.energy_score || 0), 0) / checkins.length 
    : 0;

  return (
    <ProtectedLayout title="Progress">
      <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8 fade-in">
        
        {/* Header Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 flex flex-col items-center justify-center text-center">
              <Activity className="w-5 h-5 text-primary mb-2" />
              <div className="text-2xl font-bold text-foreground">{activities.length}</div>
              <div className="text-xs text-muted-foreground uppercase tracking-wider">Activities</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex flex-col items-center justify-center text-center">
              <Calendar className="w-5 h-5 text-primary mb-2" />
              <div className="text-2xl font-bold text-foreground">{checkins.length}</div>
              <div className="text-xs text-muted-foreground uppercase tracking-wider">Check-ins</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex flex-col items-center justify-center text-center">
              <Zap className="w-5 h-5 text-primary mb-2" />
              <div className="text-2xl font-bold text-foreground">{avgEnergy.toFixed(1)}</div>
              <div className="text-xs text-muted-foreground uppercase tracking-wider">Avg Energy</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex flex-col items-center justify-center text-center">
              <TrendingUp className="w-5 h-5 text-primary mb-2" />
              <div className="text-2xl font-bold text-foreground">{Math.round(totalDuration / 60)}h {totalDuration % 60}m</div>
              <div className="text-xs text-muted-foreground uppercase tracking-wider">Total Time</div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Check-ins visualization */}
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">
            Energy Levels (Last 7 Days)
          </h2>
          <Card>
            <CardContent className="p-6">
              {checkins.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center py-4">No check-in data yet.</div>
              ) : (
                <div className="flex items-end justify-between h-32 gap-2">
                  {[...checkins].reverse().map((c) => {
                    const dateObj = new Date(c.check_in_date);
                    const dayName = dateObj.toLocaleDateString("en-US", { weekday: "short" });
                    const height = c.energy_score ? (c.energy_score / 5) * 100 : 0;
                    
                    return (
                      <div key={c.id} className="flex flex-col items-center flex-1 gap-2 group">
                        <div className="w-full relative h-full flex items-end justify-center rounded-t bg-muted/30">
                          <div 
                            className="w-full max-w-[40px] bg-primary rounded-t transition-all duration-500 relative"
                            style={{ height: `${height}%` }}
                          >
                            <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-foreground text-background text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                              {c.energy_score}/5
                            </div>
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground">{dayName}</div>
                      </div>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recent Activities List */}
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">
            Recent Activities
          </h2>
          <div className="flex flex-col gap-3">
            {activities.length === 0 ? (
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-muted-foreground">No activities logged yet.</p>
                </CardContent>
              </Card>
            ) : (
              activities.slice(0, 5).map(act => (
                <Card key={act.id}>
                  <CardContent className="p-4 flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-foreground">Activity</div>
                      <div className="text-xs text-muted-foreground mt-0.5">
                        {new Date(act.logged_date).toLocaleDateString()}
                        {act.notes ? ` • ${act.notes}` : ""}
                      </div>
                    </div>
                    {act.duration_minutes && (
                      <div className="text-sm font-medium text-primary bg-primary/10 px-3 py-1 rounded-full">
                        {act.duration_minutes} min
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>

      </div>
    </ProtectedLayout>
  );
}
