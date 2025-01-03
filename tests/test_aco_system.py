import pytest
import asyncio
from src.core.aco_system import ACOSystem

@pytest.mark.asyncio
async def test_aco_initialization():
    aco = ACOSystem(num_agents=5)
    sources = ['source1', 'source2', 'source3']
    await aco.initialize_sources(sources)
    
    assert len(aco.pheromone_matrix) == 3
    assert all(aco.pheromone_matrix[source] == 1.0 for source in sources)

@pytest.mark.asyncio
async def test_source_selection():
    aco = ACOSystem(exploration_rate=0.0)  # Disable exploration for testing
    sources = ['source1', 'source2']
    await aco.initialize_sources(sources)
    
    # Update pheromone levels
    await aco.update_pheromone('source1', 0.8)
    await aco.update_pheromone('source2', 0.2)
    
    # Test source selection
    selected_source = await aco.select_source(sources)
    assert selected_source in sources
