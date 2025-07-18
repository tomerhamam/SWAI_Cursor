import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ModulePanel from '@/components/ModulePanel.vue'
import type { Module } from '@/stores/moduleStore'
import { useModuleStore } from '@/stores/moduleStore'

describe('ModulePanel', () => {
  beforeEach(() => {
    // Create a fresh pinia instance before each test
    setActivePinia(createPinia())
  })

  const mockModule: Module = {
    name: 'TestModule',
    description: 'A test module for unit testing',
    status: 'implemented',
    version: '1.0.0',
    inputs: ['input1', 'input2'],
    outputs: ['output1'],
    dependencies: ['DependencyModule1', 'DependencyModule2']
  }

  it('renders module information when module is provided', () => {
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    expect(wrapper.find('h3').text()).toBe('TestModule')
    expect(wrapper.text()).toContain('A test module for unit testing')
    expect(wrapper.text()).toContain('implemented')
    expect(wrapper.text()).toContain('Version:')
    expect(wrapper.text()).toContain('1.0.0')
  })

  it('displays inputs correctly', () => {
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    expect(wrapper.text()).toContain('Inputs')
    const inputItems = wrapper.findAll('.section').filter(section => 
      section.find('h4').text() === 'Inputs'
    )[0].findAll('li')
    expect(inputItems).toHaveLength(2)
    expect(inputItems[0].text()).toBe('input1')
    expect(inputItems[1].text()).toBe('input2')
  })

  it('displays outputs correctly', () => {
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    expect(wrapper.text()).toContain('Outputs')
    const outputItems = wrapper.findAll('.section').filter(section => 
      section.find('h4').text() === 'Outputs'
    )[0].findAll('li')
    expect(outputItems).toHaveLength(1)
    expect(outputItems[0].text()).toBe('output1')
  })

  it('displays dependencies as clickable links', async () => {
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    const dependencyLinks = wrapper.findAll('.dependency-link')
    expect(dependencyLinks).toHaveLength(2)
    expect(dependencyLinks[0].text()).toBe('DependencyModule1')
    expect(dependencyLinks[1].text()).toBe('DependencyModule2')
  })

  it('calls store selectModule when dependency is clicked', async () => {
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    const store = useModuleStore()
    const selectModuleSpy = vi.spyOn(store, 'selectModule')

    const firstDependency = wrapper.find('.dependency-link')
    await firstDependency.trigger('click')

    expect(selectModuleSpy).toHaveBeenCalledWith('DependencyModule1')
  })

  it('emits close event when close button is clicked', async () => {
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    const closeButton = wrapper.find('.close-button')
    await closeButton.trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('handles modules with no inputs', () => {
    const moduleNoInputs = { ...mockModule, inputs: [] }
    const wrapper = mount(ModulePanel, {
      props: {
        module: moduleNoInputs
      }
    })

    // When inputs is empty array, the inputs section won't render
    const sections = wrapper.findAll('.section h4')
    const inputSection = sections.filter(h => h.text() === 'Inputs')
    expect(inputSection.length).toBe(0)
  })

  it('handles modules with no outputs', () => {
    const moduleNoOutputs = { ...mockModule, outputs: [] }
    const wrapper = mount(ModulePanel, {
      props: {
        module: moduleNoOutputs
      }
    })

    // When outputs is empty array, the outputs section won't render
    const sections = wrapper.findAll('.section h4')
    const outputSection = sections.filter(h => h.text() === 'Outputs')
    expect(outputSection.length).toBe(0)
  })

  it('handles modules with no dependencies', () => {
    const moduleNoDeps = { ...mockModule, dependencies: [] }
    const wrapper = mount(ModulePanel, {
      props: {
        module: moduleNoDeps
      }
    })

    // When dependencies is empty array, the dependencies section won't render
    const sections = wrapper.findAll('.section h4')
    const depsSection = sections.filter(h => h.text() === 'Dependencies')
    expect(depsSection.length).toBe(0)
  })

  it('applies correct status color class', () => {
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    const statusBadge = wrapper.find('.status-badge')
    expect(statusBadge.classes()).toContain('implemented')
  })

  it('handles error status correctly', () => {
    const errorModule = { ...mockModule, status: 'error' as Module['status'] }
    const wrapper = mount(ModulePanel, {
      props: {
        module: errorModule
      }
    })

    const statusBadge = wrapper.find('.status-badge')
    expect(statusBadge.classes()).toContain('error')
  })

  it('handles placeholder status correctly', () => {
    const placeholderModule = { ...mockModule, status: 'placeholder' as Module['status'] }
    const wrapper = mount(ModulePanel, {
      props: {
        module: placeholderModule
      }
    })

    const statusBadge = wrapper.find('.status-badge')
    expect(statusBadge.classes()).toContain('placeholder')
  })

  it('shows action buttons', () => {
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    expect(wrapper.find('.action-button.edit').exists()).toBe(true)
    expect(wrapper.find('.action-button.duplicate').exists()).toBe(true)
    expect(wrapper.find('.action-button.delete').exists()).toBe(true)
  })

  it('shows confirmation dialog when delete is clicked', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
    
    const wrapper = mount(ModulePanel, {
      props: {
        module: mockModule
      }
    })

    const deleteButton = wrapper.find('.action-button.delete')
    await deleteButton.trigger('click')

    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete the module "TestModule"?')
    
    confirmSpy.mockRestore()
  })
})