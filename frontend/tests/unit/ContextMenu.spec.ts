import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import ContextMenu from '@/components/ContextMenu.vue'

describe('ContextMenu', () => {
  const defaultProps = {
    visible: true,
    position: { x: 100, y: 200 },
    contextType: 'empty' as const,
    nodeId: undefined
  }

  it('renders when visible is true', () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps
    })

    expect(wrapper.find('.context-menu').exists()).toBe(true)
  })

  it('does not render when visible is false', () => {
    const wrapper = mount(ContextMenu, {
      props: {
        ...defaultProps,
        visible: false
      }
    })

    expect(wrapper.find('.context-menu').exists()).toBe(false)
  })

  it('positions menu correctly based on position prop', () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps
    })

    const menu = wrapper.find('.context-menu')
    expect(menu.attributes('style')).toContain('left: 100px')
    expect(menu.attributes('style')).toContain('top: 200px')
  })

  it('shows correct menu items for empty context', () => {
    const wrapper = mount(ContextMenu, {
      props: {
        ...defaultProps,
        contextType: 'empty'
      }
    })

    const menuItems = wrapper.findAll('.menu-item')
    expect(menuItems[0].text()).toContain('Add Module')
    expect(menuItems[1].text()).toContain('Dependency Mode')
    expect(menuItems[2].text()).toContain('Paste')
  })

  it('shows correct menu items for node context', () => {
    const wrapper = mount(ContextMenu, {
      props: {
        ...defaultProps,
        contextType: 'node',
        nodeId: 'TestModule'
      }
    })

    const menuItems = wrapper.findAll('.menu-item')
    expect(menuItems[0].text()).toContain('Edit Module')
    expect(menuItems[1].text()).toContain('Duplicate')
    expect(menuItems[2].text()).toContain('Delete')
    // Separator at index 3
    expect(menuItems[3].classes()).toContain('menu-separator')
    expect(menuItems[4].text()).toContain('Start Dependency')
    expect(menuItems[5].text()).toContain('View Details')
  })

  it('emits menuAction event when item is clicked', async () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps
    })

    const firstMenuItem = wrapper.find('.menu-item')
    await firstMenuItem.trigger('click')

    expect(wrapper.emitted('menuAction')).toBeTruthy()
    expect(wrapper.emitted('menuAction')![0]).toEqual(['add-module', undefined])
  })

  it('emits close event when item is clicked', async () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps
    })

    const firstMenuItem = wrapper.find('.menu-item')
    await firstMenuItem.trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('includes nodeId in menuAction event for node context', async () => {
    const wrapper = mount(ContextMenu, {
      props: {
        ...defaultProps,
        contextType: 'node',
        nodeId: 'TestModule'
      }
    })

    const firstMenuItem = wrapper.find('.menu-item')
    await firstMenuItem.trigger('click')

    expect(wrapper.emitted('menuAction')![0]).toEqual(['edit-module', 'TestModule'])
  })

  it('does not emit events for disabled items', async () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps
    })

    // Paste item is disabled
    const pasteItem = wrapper.findAll('.menu-item')[2]
    expect(pasteItem.classes()).toContain('menu-item-disabled')
    
    await pasteItem.trigger('click')
    
    expect(wrapper.emitted('menuAction')).toBeFalsy()
    expect(wrapper.emitted('close')).toBeFalsy()
  })

  it('handles keyboard navigation with arrow keys', async () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps,
      attachTo: document.body
    })

    const menu = wrapper.find('.context-menu')
    
    // Trigger arrow down
    await menu.trigger('keydown', { key: 'ArrowDown' })
    await nextTick()
    
    // Should focus second item
    const menuItems = wrapper.findAll('.menu-item')
    expect(document.activeElement).toBe(menuItems[1].element)

    wrapper.unmount()
  })

  it('closes menu on Escape key', async () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps
    })

    const menu = wrapper.find('.context-menu')
    await menu.trigger('keydown', { key: 'Escape' })

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('triggers action on Enter key', async () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps,
      attachTo: document.body
    })

    const firstMenuItem = wrapper.find('.menu-item')
    firstMenuItem.element.focus()
    
    await firstMenuItem.trigger('keydown', { key: 'Enter' })

    expect(wrapper.emitted('menuAction')).toBeTruthy()
    expect(wrapper.emitted('close')).toBeTruthy()

    wrapper.unmount()
  })

  it('triggers action on Space key', async () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps,
      attachTo: document.body
    })

    const firstMenuItem = wrapper.find('.menu-item')
    firstMenuItem.element.focus()
    
    await firstMenuItem.trigger('keydown', { key: ' ' })

    expect(wrapper.emitted('menuAction')).toBeTruthy()
    expect(wrapper.emitted('close')).toBeTruthy()

    wrapper.unmount()
  })

  it('displays menu icons correctly', () => {
    const wrapper = mount(ContextMenu, {
      props: defaultProps
    })

    const icons = wrapper.findAll('.menu-icon')
    expect(icons[0].text()).toBe('➕')
    expect(icons[1].text()).toBe('🔗')
    expect(icons[2].text()).toBe('📋')
  })

  it('handles menu separators correctly', () => {
    const wrapper = mount(ContextMenu, {
      props: {
        ...defaultProps,
        contextType: 'node',
        nodeId: 'TestModule'
      }
    })

    const separator = wrapper.find('.menu-separator')
    expect(separator.exists()).toBe(true)
    expect(separator.attributes('role')).toBe('separator')
  })

  it('applies correct ARIA attributes', () => {
    const wrapper = mount(ContextMenu, {
      props: {
        ...defaultProps,
        contextType: 'node',
        nodeId: 'TestModule'
      }
    })

    const menu = wrapper.find('.context-menu')
    expect(menu.attributes('role')).toBe('menu')
    expect(menu.attributes('aria-label')).toContain('TestModule')

    const menuItems = wrapper.findAll('.menu-item')
    menuItems.forEach(item => {
      if (!item.classes().includes('menu-separator')) {
        expect(item.attributes('role')).toBe('menuitem')
      }
    })
  })
})