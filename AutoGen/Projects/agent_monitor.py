<<<<<<< HEAD
"""
Real-Time Agent Status Monitoring
==================================
This module adds real-time status polling for sequential agent execution
"""

import streamlit as st
import requests
import time
from typing import Dict, Optional

class AgentStatusMonitor:
    """Monitor and display real-time agent execution status"""
    
    def __init__(self, flask_url: str):
        self.flask_url = flask_url
        self.agent_sequence = ['research', 'writer', 'seo', 'scorer']
        
    def simulate_real_time_execution(self, workflow_id: str, total_estimated_time: float = 60.0):
        """
        Simulate real-time agent execution with realistic timing
        
        Args:
            workflow_id: Unique workflow identifier
            total_estimated_time: Total estimated execution time in seconds
        """
        # Agent execution time distribution (percentage of total)
        agent_timing = {
            'research': 0.25,   # 25% of total time
            'writer': 0.40,     # 40% of total time
            'seo': 0.20,        # 20% of total time
            'scorer': 0.15      # 15% of total time
        }
        
        start_time = time.time()
        
        for agent_name in self.agent_sequence:
            # Mark agent as active
            st.session_state.agent_status[agent_name] = 'active'
            agent_start = time.time()
            
            # Calculate estimated time for this agent
            estimated_duration = total_estimated_time * agent_timing[agent_name]
            
            # Show progress with updates every 0.5 seconds
            progress_container = st.empty()
            status_text = st.empty()
            
            elapsed = 0
            while elapsed < estimated_duration:
                progress = min(elapsed / estimated_duration, 1.0)
                
                with progress_container.container():
                    st.progress(progress, text=f"Processing {agent_name.title()} Agent...")
                
                status_text.info(f"⏱️ {agent_name.title()} Agent: {elapsed:.1f}s / ~{estimated_duration:.1f}s")
                
                time.sleep(0.5)
                elapsed = time.time() - agent_start
            
            # Mark agent as completed
            actual_time = time.time() - agent_start
            st.session_state.agent_status[agent_name] = 'completed'
            st.session_state.agent_times[agent_name] = actual_time
            
            progress_container.empty()
            status_text.success(f"✅ {agent_name.title()} Agent completed in {actual_time:.1f}s")
            
            # Small delay between agents
            time.sleep(0.5)
        
        return time.time() - start_time


def create_streaming_workflow_monitor():
    """
    Create a real-time workflow monitor that shows sequential agent execution
    """
    st.markdown("### 🔄 Real-Time Workflow Execution")
    
    # Create containers for each agent
    agent_containers = {}
    agent_info = [
        {'name': 'research', 'icon': '🔍', 'title': 'Research Agent'},
        {'name': 'writer', 'icon': '✍️', 'title': 'Content Writer Agent'},
        {'name': 'seo', 'icon': '📊', 'title': 'SEO Validation Agent'},
        {'name': 'scorer', 'icon': '🎯', 'title': 'Quality Scorer Agent'}
    ]
    
    for agent in agent_info:
        container = st.container()
        with container:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{agent['icon']} {agent['title']}**")
            
            with col2:
                status_placeholder = st.empty()
                status_placeholder.info("⏳ Waiting...")
            
            with col3:
                time_placeholder = st.empty()
                time_placeholder.text("--")
            
            agent_containers[agent['name']] = {
                'status': status_placeholder,
                'time': time_placeholder
            }
    
    return agent_containers


def update_agent_display(agent_containers: Dict, agent_name: str, status: str, elapsed_time: Optional[float] = None):
    """Update agent display in real-time"""
    
    container = agent_containers.get(agent_name)
    if not container:
        return
    
    if status == 'active':
        container['status'].warning("🔵 Processing...")
    elif status == 'completed':
        container['status'].success("✅ Completed")
        if elapsed_time:
            container['time'].text(f"{elapsed_time:.1f}s")
    elif status == 'error':
        container['status'].error("❌ Error")
    else:
        container['status'].info("⏳ Pending")
=======
"""
Real-Time Agent Status Monitoring
==================================
This module adds real-time status polling for sequential agent execution
"""

import streamlit as st
import requests
import time
from typing import Dict, Optional

class AgentStatusMonitor:
    """Monitor and display real-time agent execution status"""
    
    def __init__(self, flask_url: str):
        self.flask_url = flask_url
        self.agent_sequence = ['research', 'writer', 'seo', 'scorer']
        
    def simulate_real_time_execution(self, workflow_id: str, total_estimated_time: float = 60.0):
        """
        Simulate real-time agent execution with realistic timing
        
        Args:
            workflow_id: Unique workflow identifier
            total_estimated_time: Total estimated execution time in seconds
        """
        # Agent execution time distribution (percentage of total)
        agent_timing = {
            'research': 0.25,   # 25% of total time
            'writer': 0.40,     # 40% of total time
            'seo': 0.20,        # 20% of total time
            'scorer': 0.15      # 15% of total time
        }
        
        start_time = time.time()
        
        for agent_name in self.agent_sequence:
            # Mark agent as active
            st.session_state.agent_status[agent_name] = 'active'
            agent_start = time.time()
            
            # Calculate estimated time for this agent
            estimated_duration = total_estimated_time * agent_timing[agent_name]
            
            # Show progress with updates every 0.5 seconds
            progress_container = st.empty()
            status_text = st.empty()
            
            elapsed = 0
            while elapsed < estimated_duration:
                progress = min(elapsed / estimated_duration, 1.0)
                
                with progress_container.container():
                    st.progress(progress, text=f"Processing {agent_name.title()} Agent...")
                
                status_text.info(f"⏱️ {agent_name.title()} Agent: {elapsed:.1f}s / ~{estimated_duration:.1f}s")
                
                time.sleep(0.5)
                elapsed = time.time() - agent_start
            
            # Mark agent as completed
            actual_time = time.time() - agent_start
            st.session_state.agent_status[agent_name] = 'completed'
            st.session_state.agent_times[agent_name] = actual_time
            
            progress_container.empty()
            status_text.success(f"✅ {agent_name.title()} Agent completed in {actual_time:.1f}s")
            
            # Small delay between agents
            time.sleep(0.5)
        
        return time.time() - start_time


def create_streaming_workflow_monitor():
    """
    Create a real-time workflow monitor that shows sequential agent execution
    """
    st.markdown("### 🔄 Real-Time Workflow Execution")
    
    # Create containers for each agent
    agent_containers = {}
    agent_info = [
        {'name': 'research', 'icon': '🔍', 'title': 'Research Agent'},
        {'name': 'writer', 'icon': '✍️', 'title': 'Content Writer Agent'},
        {'name': 'seo', 'icon': '📊', 'title': 'SEO Validation Agent'},
        {'name': 'scorer', 'icon': '🎯', 'title': 'Quality Scorer Agent'}
    ]
    
    for agent in agent_info:
        container = st.container()
        with container:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{agent['icon']} {agent['title']}**")
            
            with col2:
                status_placeholder = st.empty()
                status_placeholder.info("⏳ Waiting...")
            
            with col3:
                time_placeholder = st.empty()
                time_placeholder.text("--")
            
            agent_containers[agent['name']] = {
                'status': status_placeholder,
                'time': time_placeholder
            }
    
    return agent_containers


def update_agent_display(agent_containers: Dict, agent_name: str, status: str, elapsed_time: Optional[float] = None):
    """Update agent display in real-time"""
    
    container = agent_containers.get(agent_name)
    if not container:
        return
    
    if status == 'active':
        container['status'].warning("🔵 Processing...")
    elif status == 'completed':
        container['status'].success("✅ Completed")
        if elapsed_time:
            container['time'].text(f"{elapsed_time:.1f}s")
    elif status == 'error':
        container['status'].error("❌ Error")
    else:
        container['status'].info("⏳ Pending")
>>>>>>> c48496b (Automated update)
