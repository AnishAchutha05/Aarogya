"use client";

import Image, { type StaticImageData } from "next/image";
import { BadgeCheck, MessageCircle, Repeat2, Heart, Share } from "lucide-react";
import { Lens } from "@/components/ui/lens";

interface CommunityTweetCardProps {
  author: string;
  handle: string;
  initials: string;
  text: string;
  image: StaticImageData;
  imageAlt: string;
  isBrandNote?: boolean;
  priority?: boolean;
}

export function CommunityTweetCard({
  author,
  handle,
  initials,
  text,
  image,
  imageAlt,
  isBrandNote = false,
  priority = false,
}: CommunityTweetCardProps) {
  return (
    <article className="mx-auto w-full max-w-[540px] overflow-hidden rounded-xl border border-[#d7dce1] bg-white text-[#0f1419] shadow-sm">
      <div className="flex items-center gap-3 px-4 pt-4">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#e8f3ec] text-xs font-semibold text-[#0B6623] ring-1 ring-black/5">
          {initials}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <span className="truncate text-sm font-bold text-[#0f1419]">{author}</span>
            <BadgeCheck className="h-4 w-4 shrink-0 fill-[#1d9bf0] text-white" aria-label="Verified account" />
          </div>
          <p className="truncate text-sm text-[#536471]">{handle}</p>
        </div>
        <svg aria-hidden="true" viewBox="0 0 24 24" className="h-[18px] w-[18px] shrink-0 fill-[#536471]">
          <path d="M22.162 5.656a8.384 8.384 0 0 1-2.402.658A4.196 4.196 0 0 0 21.6 4c-.82.488-1.719.83-2.656 1.015a4.182 4.182 0 0 0-7.126 3.814 11.874 11.874 0 0 1-8.62-4.37 4.168 4.168 0 0 0-.566 2.103c0 1.45.738 2.731 1.86 3.481a4.168 4.168 0 0 1-1.894-.523v.052a4.185 4.185 0 0 0 3.355 4.101 4.21 4.21 0 0 1-1.89.072A4.185 4.185 0 0 0 7.97 16.65a8.394 8.394 0 0 1-6.191 1.732 11.83 11.83 0 0 0 6.41 1.88c7.693 0 11.9-6.373 11.9-11.9 0-.18-.005-.362-.013-.54a8.496 8.496 0 0 0 2.087-2.165z" />
        </svg>
      </div>

      <p className="px-4 pb-4 pt-3 text-[15px] leading-[1.45] text-[#0f1419]">{text}</p>

      <div className="mx-4 overflow-hidden rounded-xl border border-[#cfd9de] bg-white">
        <Lens zoomFactor={1.8} lensSize={150} ariaLabel={`Zoom into image: ${imageAlt}`}>
          <Image
            src={image}
            alt={imageAlt}
            className="block h-auto w-full object-contain"
            sizes="(max-width: 1024px) 88vw, 508px"
            priority={priority}
          />
        </Lens>
        {isBrandNote && (
          <span className="block px-3 py-2 text-xs text-[#536471]">
            A thought from Aarogya
          </span>
        )}
      </div>

      <div className="flex items-center justify-between px-7 py-4 text-[#657786]" aria-hidden="true">
        <MessageCircle className="h-[17px] w-[17px]" />
        <Repeat2 className="h-[17px] w-[17px]" />
        <Heart className="h-[17px] w-[17px]" />
        <Share className="h-[17px] w-[17px]" />
      </div>
    </article>
  );
}
