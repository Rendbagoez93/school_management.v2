| Pattern | Category | Use When... | Watch Out For... |
|---------|----------|-------------|------------------|
| Factory Method | Creational | Creating objects without knowing exact class | Over-abstraction |
| Abstract Factory | Creational | Families of related products | Complex when simple Factory works |
| Builder | Creational | Many optional params, step-by-step construction | Premature for simple objects |
| Singleton | Creational | Exactly one instance, global access | Testing difficulties, hidden deps |
| Prototype | Creational | Clone existing objects, runtime specification | Deep copy complexity |
| Adapter | Structural | Incompatible interfaces need integration | Overengineering simple cases |
| Decorator | Structural | Add responsibilities dynamically | Too many decorators = hard to debug |
| Facade | Structural | Simplify complex subsystem | Becoming a "god object" |
| Proxy | Structural | Control access to object | Added indirection overhead |
| Composite | Structural | Tree structures, treat parts uniformly | Overly uniform interface |
| Observer | Behavioral | One-to-many notification | Circular updates, memory leaks |
| Strategy | Behavioral | Interchangeable algorithms | If/else explosion of strategies |
| Command | Behavioral | Queue/undo operations | Overhead for simple actions |
| State | Behavioral | Behavior changes with internal state | State explosion |
| Iterator | Behavioral | Custom traversal without exposing structure | Python usually has built-in |
| Template Method | Behavioral | Algorithm with customizable steps | Inheritance rigidity |
| Chain of Responsibility | Behavioral | Multiple handlers, handler unknown | Hard to follow execution flow |

## Quick Pattern Selection Flowchart

**Does it involve OBJECT CREATION?** → Creational
- One class, unknown at runtime? → **Factory Method**
- Family of related products? → **Abstract Factory**
- Complex construction with steps? → **Builder**
- Clone existing object? → **Prototype**
- Only one instance allowed? → **Singleton** (carefully)

**Does it involve OBJECT COMPOSITION?** → Structural
- Incompatible interfaces? → **Adapter**
- Add responsibilities dynamically? → **Decorator**
- Simplify complex subsystem? → **Facade**
- Control/instrument access? → **Proxy**
- Tree structure needed? → **Composite**

**Does it involve OBJECT COMMUNICATION?** → Behavioral
- Notify many of state change? → **Observer**
- Switch algorithms at runtime? → **Strategy**
- Undo/redo or queue actions? → **Command**
- Behavior varies by state? → **State**
- Hand-off request to chain? → **Chain of Responsibility**
- Algorithm skeleton variation? → **Template Method**