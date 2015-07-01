
from simulation import ComponentType

ComponentType.MouseControlled = ComponentType.FirstUserComponent
ComponentType.Follow = ComponentType( ComponentType.MouseControlled+1 )
ComponentType.Light = ComponentType( ComponentType.Follow+1 )
ComponentType.LightShaderData = ComponentType( ComponentType.Light+1 )

ComponentType.LogicAI = ComponentType( ComponentType.LightShaderData+1 )
ComponentType.Player = ComponentType( ComponentType.LogicAI+1 )
ComponentType.Tile = ComponentType( ComponentType.Player+1 )
ComponentType.Tilemap = ComponentType( ComponentType.Tile+1 )
ComponentType.Action = ComponentType( ComponentType.Tilemap+1 )
ComponentType.Car = ComponentType( ComponentType.Action+1 )
ComponentType.Physics = ComponentType( ComponentType.Car+1 )
ComponentType.Trigger = ComponentType( ComponentType.Physics+1 )
ComponentType.Pedestrian = ComponentType( ComponentType.Trigger+1 )
ComponentType.Inventory = ComponentType( ComponentType.Pedestrian+1 )
ComponentType.Pickup = ComponentType( ComponentType.Inventory+1 )
ComponentType.Bullet = ComponentType( ComponentType.Pickup+1 )
ComponentType.Health = ComponentType( ComponentType.Bullet+1 )
ComponentType.Animation = ComponentType( ComponentType.Health+1 )

FinalRenderFlag = 1 << 0
ShadowRenderFlag = 1 << 1

