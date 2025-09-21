import { Camera, PiIcon as AIIcon, DollarSign } from "lucide-react"
import Image from "next/image"

const features = [
  {
    name: "Universal Paper-to-MIDI Interface",
    description:
      "Transform any sheet of paper into a powerful, fully-responsive MIDI instrument using just your webcam—no special hardware required.",
    icon: Camera,
  },
  {
    name: "AI-Powered Music Teacher",
    description:
      "Get real-time, personalized feedback and guided lessons from an adaptive AI music coach, supporting learners from first notes to full performance.",
    icon: AIIcon,
  },
  {
    name: "Instant Song Transcription",
    description:
      "Convert any audio or instrumental track into an easy-to-play paper layout, making favorite songs accessible to all—no reading traditional sheet music needed.",
    icon: () => (
      <Image
        src="/images/lead-zeppelin-logo.png"
        alt="Lead Zeppelin Logo"
        width={32}
        height={32}
        className="h-8 w-8"
        style={{
          filter:
            "brightness(0) saturate(100%) invert(12%) sepia(89%) saturate(2851%) hue-rotate(346deg) brightness(95%) contrast(95%)",
        }}
      />
    ),
  },
  {
    name: "Zero Cost, Infinite Creativity",
    description:
      "Experience professional music education and creation tools for free—no expensive instruments, subscriptions, or barriers. Every student, everywhere, can compose and perform.",
    icon: DollarSign,
  },
]

export default function Features() {
  return (
    <section className="container mx-auto px-4 space-y-16 py-24 md:py-32">
      <div className="mx-auto max-w-[58rem] text-center">
        <h2 className="font-bold text-3xl leading-[1.1] sm:text-3xl md:text-5xl">Simplicity at its Finest</h2>
        <p className="mt-4 text-muted-foreground sm:text-lg">
          Explore how Lead Zeppelin can turn pen and paper into a wonderful instrument.
        </p>
      </div>
      <div className="mx-auto grid max-w-5xl grid-cols-1 gap-8 md:grid-cols-2">
        {features.map((feature) => (
          <div key={feature.name} className="relative overflow-hidden rounded-lg border bg-background p-8">
            <div className="flex items-center gap-4">
              {typeof feature.icon === "function" ? <feature.icon /> : <feature.icon className="h-8 w-8" />}
              <h3 className="font-bold">{feature.name}</h3>
            </div>
            <p className="mt-2 text-muted-foreground">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
