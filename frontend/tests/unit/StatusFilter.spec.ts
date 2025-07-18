import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusFilter from '@/components/StatusFilter.vue'
import type { Module } from '@/stores/moduleStore'

describe('StatusFilter', () => {
  const mockModules: Record<string, Module> = {
    module1: {
      name: 'Module1',
      description: 'Test module 1',
      status: 'implemented',
      version: '1.0.0',
      inputs: [],
      outputs: [],
      dependencies: []
    },
    module2: {
      name: 'Module2',
      description: 'Test module 2',
      status: 'placeholder',
      version: '1.0.0',
      inputs: [],
      outputs: [],
      dependencies: []
    },
    module3: {
      name: 'Module3',
      description: 'Test module 3',
      status: 'error',
      version: '1.0.0',
      inputs: [],
      outputs: [],
      dependencies: []
    },
    module4: {
      name: 'Module4',
      description: 'Test module 4',
      status: 'implemented',
      version: '1.0.0',
      inputs: [],
      outputs: [],
      dependencies: []
    }
  }

  it('renders all status options as buttons', () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    const buttons = wrapper.findAll('.filter-btn')
    expect(buttons).toHaveLength(4) // All + implemented, placeholder, error

    expect(buttons[0].text()).toContain('All (4)')
    expect(buttons[1].text()).toContain('Implemented (2)')
    expect(buttons[2].text()).toContain('Placeholder (1)')
    expect(buttons[3].text()).toContain('Error (1)')
  })

  it('displays correct counts for each status', () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    const buttons = wrapper.findAll('.filter-btn')
    expect(buttons[1].text()).toContain('(2)') // 2 implemented
    expect(buttons[2].text()).toContain('(1)') // 1 placeholder
    expect(buttons[3].text()).toContain('(1)') // 1 error
  })

  it('emits filter-change event when status button is clicked', async () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    const implementedButton = wrapper.findAll('.filter-btn')[1]
    await implementedButton.trigger('click')

    expect(wrapper.emitted('filterChange')).toBeTruthy()
    const emittedSet = wrapper.emitted('filterChange')![0][0] as Set<string>
    expect(emittedSet).toBeInstanceOf(Set)
    expect(emittedSet.has('implemented')).toBe(true)
  })

  it('toggles button active state when clicked', async () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    const implementedButton = wrapper.findAll('.filter-btn')[1]
    
    // Initially not active
    expect(implementedButton.classes()).not.toContain('active')
    
    // Click to activate
    await implementedButton.trigger('click')
    expect(implementedButton.classes()).toContain('active')
    
    // Click again to deactivate
    await implementedButton.trigger('click')
    expect(implementedButton.classes()).not.toContain('active')
  })

  it('allows multiple statuses to be selected', async () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    const buttons = wrapper.findAll('.filter-btn')
    await buttons[1].trigger('click') // implemented
    await buttons[2].trigger('click') // placeholder

    const emittedEvents = wrapper.emitted('filterChange')!
    const lastEmittedSet = emittedEvents[emittedEvents.length - 1][0] as Set<string>
    
    expect(lastEmittedSet.size).toBe(2)
    expect(lastEmittedSet.has('implemented')).toBe(true)
    expect(lastEmittedSet.has('placeholder')).toBe(true)
  })

  it('shows all modules when "All" button is clicked', async () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    const buttons = wrapper.findAll('.filter-btn')
    
    // Select some filters first
    await buttons[1].trigger('click') // implemented
    await buttons[2].trigger('click') // placeholder
    
    // Click "All" button
    await buttons[0].trigger('click')

    const emittedEvents = wrapper.emitted('filterChange')!
    const lastEmittedSet = emittedEvents[emittedEvents.length - 1][0] as Set<string>
    
    expect(lastEmittedSet.size).toBe(0)
    expect(buttons[0].classes()).toContain('active')
  })

  it('shows "All" button as active when no filters selected', () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    const allButton = wrapper.findAll('.filter-btn')[0]
    expect(allButton.classes()).toContain('active')
  })

  it('handles empty modules object', () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: {}
      }
    })

    expect(wrapper.text()).toContain('All (0)')
    const buttons = wrapper.findAll('.filter-btn')
    expect(buttons).toHaveLength(4) // Still shows all status options
  })

  it('applies correct status colors to active buttons', async () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    const buttons = wrapper.findAll('.filter-btn')
    
    // Click implemented button
    await buttons[1].trigger('click')
    expect(buttons[1].classes()).toContain('implemented')
    expect(buttons[1].classes()).toContain('active')
    
    // Click placeholder button
    await buttons[2].trigger('click')
    expect(buttons[2].classes()).toContain('placeholder')
    expect(buttons[2].classes()).toContain('active')
    
    // Click error button
    await buttons[3].trigger('click')
    expect(buttons[3].classes()).toContain('error')
    expect(buttons[3].classes()).toContain('active')
  })

  it('updates counts when modules prop changes', async () => {
    const wrapper = mount(StatusFilter, {
      props: {
        modules: mockModules
      }
    })

    expect(wrapper.text()).toContain('All (4)')
    
    // Update modules
    const newModules = {
      module1: mockModules.module1,
      module2: mockModules.module2
    }
    
    await wrapper.setProps({ modules: newModules })
    
    expect(wrapper.text()).toContain('All (2)')
    expect(wrapper.text()).toContain('Implemented (1)')
    expect(wrapper.text()).toContain('Placeholder (1)')
    expect(wrapper.text()).toContain('Error (0)')
  })
})