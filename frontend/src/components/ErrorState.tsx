export function ErrorState({ message }: { message: string }) {
  return (
    <div className="mx-auto max-w-md rounded-xl border border-red-900/50 bg-red-950/30 px-6 py-8 text-center">
      <p className="text-red-300">{message}</p>
    </div>
  )
}
