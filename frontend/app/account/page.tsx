"use client";

import React, { useState, useEffect } from "react";
import { ProtectedLayout } from "@/components/layout/protected-layout";
import { useAuth } from "@/contexts/auth-context";
import { usersService } from "@/lib/services/users";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import type { ProfileResponse, ProfileUpdate } from "@/types";

export default function AccountPage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState<Partial<ProfileUpdate>>({});
  const [dietary, setDietary] = useState("");
  const [foods, setFoods] = useState("");

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await usersService.getProfile();
        setProfile(data);
        setFormData({
          dob: data.dob || "",
          gender: data.gender || "",
          height_cm: data.height_cm,
          weight_kg: data.weight_kg,
          nationality: data.nationality || "",
          region: data.region || "",
          activity_level: data.activity_level || "",
        });
        
        let d = [];
        if (data.dietary_preferences) {
          try { d = JSON.parse(data.dietary_preferences); } catch {}
        }
        setDietary(d.join(", "));
        
        let f = [];
        if (data.commonly_eaten_foods) {
          try { f = JSON.parse(data.commonly_eaten_foods); } catch {}
        }
        setFoods(f.join(", "));
      } catch (err) {
        // error
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === "number" ? (value ? Number(value) : undefined) : value
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const updateData: ProfileUpdate = {
        ...formData,
        dietary_preferences: dietary ? dietary.split(",").map(s => s.trim()).filter(Boolean) : [],
        commonly_eaten_foods: foods ? foods.split(",").map(s => s.trim()).filter(Boolean) : [],
      };
      const updated = await usersService.updateProfile(updateData);
      setProfile(updated);
    } catch {
      // error
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <ProtectedLayout title="Account">
        <div className="flex h-[50vh] items-center justify-center">
          <Spinner className="text-primary" />
        </div>
      </ProtectedLayout>
    );
  }

  return (
    <ProtectedLayout title="Account">
      <div className="max-w-2xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 fade-in">
        <Card>
          <CardHeader>
            <CardTitle>User Details</CardTitle>
            <CardDescription>Your core account information.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <label className="text-xs font-medium text-muted-foreground uppercase">Email</label>
              <Input disabled value={user?.email || ""} className="bg-muted/50" />
            </div>
            <div className="grid gap-2">
              <label className="text-xs font-medium text-muted-foreground uppercase">Name</label>
              <Input disabled value={user?.name || ""} className="bg-muted/50" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Health Profile</CardTitle>
            <CardDescription>Update your biological and regional details to improve personalization.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground uppercase">Date of Birth</label>
                <Input type="date" name="dob" value={formData.dob || ""} onChange={handleChange} />
              </div>
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground uppercase">Gender</label>
                <Input name="gender" placeholder="e.g. Male, Female" value={formData.gender || ""} onChange={handleChange} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground uppercase">Height (cm)</label>
                <Input type="number" name="height_cm" value={formData.height_cm || ""} onChange={handleChange} />
              </div>
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground uppercase">Weight (kg)</label>
                <Input type="number" name="weight_kg" value={formData.weight_kg || ""} onChange={handleChange} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground uppercase">Nationality</label>
                <Input name="nationality" value={formData.nationality || ""} onChange={handleChange} />
              </div>
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground uppercase">Region</label>
                <Input name="region" value={formData.region || ""} onChange={handleChange} />
              </div>
            </div>
            <div className="grid gap-2">
              <label className="text-xs font-medium text-muted-foreground uppercase">Dietary Preferences</label>
              <Input placeholder="Vegetarian, Gluten-free..." value={dietary} onChange={(e) => setDietary(e.target.value)} />
              <p className="text-xs text-muted-foreground">Comma-separated</p>
            </div>
            <div className="grid gap-2">
              <label className="text-xs font-medium text-muted-foreground uppercase">Common Foods</label>
              <Input placeholder="Rice, Chicken..." value={foods} onChange={(e) => setFoods(e.target.value)} />
              <p className="text-xs text-muted-foreground">Comma-separated</p>
            </div>
            <div className="pt-4">
              <Button onClick={handleSave} disabled={saving} className="bg-primary text-primary-foreground">
                {saving ? <Spinner className="w-4 h-4 mr-2" /> : null}
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </ProtectedLayout>
  );
}
