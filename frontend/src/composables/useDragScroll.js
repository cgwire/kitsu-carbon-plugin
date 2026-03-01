import { watch, onBeforeUnmount } from 'vue'

export function useDragScroll(containerRef) {
  let isDown = false
  let startX = 0
  let startY = 0
  let scrollLeft = 0
  let scrollTop = 0
  let currentEl = null

  const onMouseDown = (e) => {
    if (!currentEl) return
    isDown = true
    startX = e.pageX - currentEl.offsetLeft
    startY = e.pageY - currentEl.offsetTop
    scrollLeft = currentEl.scrollLeft
    scrollTop = currentEl.scrollTop
    currentEl.style.cursor = 'grabbing'
    currentEl.style.userSelect = 'none'
  }

  const onMouseUp = () => {
    if (!currentEl) return
    isDown = false
    currentEl.style.cursor = 'grab'
    currentEl.style.removeProperty('user-select')
  }

  const onMouseMove = (e) => {
    if (!isDown || !currentEl) return
    e.preventDefault()
    const x = e.pageX - currentEl.offsetLeft
    const y = e.pageY - currentEl.offsetTop
    currentEl.scrollLeft = scrollLeft - (x - startX)
    currentEl.scrollTop = scrollTop - (y - startY)
  }

  const onMouseLeave = () => {
    if (isDown) onMouseUp()
  }

  const attach = (el) => {
    el.style.cursor = 'grab'
    el.addEventListener('mousedown', onMouseDown)
    el.addEventListener('mouseup', onMouseUp)
    el.addEventListener('mousemove', onMouseMove)
    el.addEventListener('mouseleave', onMouseLeave)
  }

  const detach = (el) => {
    el.removeEventListener('mousedown', onMouseDown)
    el.removeEventListener('mouseup', onMouseUp)
    el.removeEventListener('mousemove', onMouseMove)
    el.removeEventListener('mouseleave', onMouseLeave)
  }

  watch(containerRef, (newEl, oldEl) => {
    if (oldEl) {
      detach(oldEl)
      isDown = false
    }
    currentEl = newEl
    if (newEl) {
      attach(newEl)
    }
  })

  onBeforeUnmount(() => {
    if (currentEl) {
      detach(currentEl)
      currentEl = null
    }
  })
}
