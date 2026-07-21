<script>
  let { value = 0, suffix = '', label = '', source = '' } = $props()
  let display = $state(0)
  let el = $state(null)

  $effect(() => {
    if (!el) return
    const obs = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            animate()
            obs.unobserve(el)
          }
        }
      },
      { threshold: 0.3 },
    )
    obs.observe(el)
    return () => obs.disconnect()
  })

  function animate() {
    const duration = 1600
    const start = performance.now()
    function frame(now) {
      const t = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - t, 3)
      display = Math.round(eased * value)
      if (t < 1) requestAnimationFrame(frame)
    }
    requestAnimationFrame(frame)
  }
</script>

<div bind:this={el} class="flex flex-col items-center text-center">
  <span class="text-[2.75rem] md:text-5xl font-display font-extrabold text-accent tabular-nums leading-none">
    {display}{suffix}
  </span>
  <span class="text-sm md:text-base text-muted mt-2 leading-snug">{label}</span>
  {#if source}
    <span class="text-[11px] text-muted/60 mt-1.5 italic">{source}</span>
  {/if}
</div>
