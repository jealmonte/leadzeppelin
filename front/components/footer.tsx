export default function Footer() {
  return (
    <footer>
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        <p className="text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} Lead Zeppelin, Inc. All rights reserved.
        </p>
      </div>
    </footer>
  )
}
