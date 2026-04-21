# Structural Patterns

Patterns for composing classes and objects into larger structures.

---

## Adapter

**Intent:** Convert interface of one class to another interface clients expect  
**Use when:** Integrating with incompatible existing code

### AI Pseudocode
```
INTERFACE Target {
  FN request(): str
}

CLASS Adaptee {
  FN specificRequest(): str {
    RETURN "Special data"
  }
}

CLASS Adapter IMPLEMENTS Target {
  -adaptee: Adaptee
  
  CONSTRUCTOR(a: Adaptee) {
    this.adaptee = a
  }
  
  FN request(): str {
    RETURN this.adaptee.specificRequest()
  }
}
```

### TypeScript
```typescript
interface Target {
  request(): string;
}

class Adaptee {
  specificRequest(): string {
    return "Special data";
  }
}

class Adapter implements Target {
  constructor(private adaptee: Adaptee) {}
  
  request(): string {
    return this.adaptee.specificRequest();
  }
}
```

### Rust
```rust
trait Target {
    fn request(&self) -> String;
}

struct Adaptee;
impl Adaptee {
    fn specific_request(&self) -> String {
        "Special data".to_string()
    }
}

struct Adapter {
    adaptee: Adaptee,
}

impl Target for Adapter {
    fn request(&self) -> String {
        self.adaptee.specific_request()
    }
}
```

### Java
```java
interface Target {
    String request();
}

class Adaptee {
    String specificRequest() {
        return "Special data";
    }
}

class Adapter implements Target {
    private Adaptee adaptee;
    
    Adapter(Adaptee adaptee) {
        this.adaptee = adaptee;
    }
    
    public String request() {
        return adaptee.specificRequest();
    }
}
```

### Python
```python
from abc import ABC, abstractmethod

class Target(ABC):
    @abstractmethod
    def request(self) -> str: pass

class Adaptee:
    def specific_request(self) -> str:
        return "Special data"

class Adapter(Target):
    def __init__(self, adaptee: Adaptee):
        self._adaptee = adaptee
    
    def request(self) -> str:
        return self._adaptee.specific_request()
```

**When to use:**
- Want to use existing class with incompatible interface
- Create reusable class that cooperates with unforeseen classes
- Need to adapt several subclasses (object adapter preferred)

---

## Decorator

**Intent:** Add responsibilities to objects dynamically  
**Use when:** Extending behavior without subclassing

### AI Pseudocode
```
INTERFACE Component {
  FN operation(): str
}

CLASS ConcreteComponent IMPLEMENTS Component {
  FN operation(): str {
    RETURN "ConcreteComponent"
  }
}

CLASS Decorator IMPLEMENTS Component {
  -component: Component
  
  CONSTRUCTOR(c: Component) {
    this.component = c
  }
  
  FN operation(): str {
    RETURN this.component.operation()
  }
}

CLASS ConcreteDecorator EXTENDS Decorator {
  CONSTRUCTOR(c: Component) {
    SUPER(c)
  }
  
  FN operation(): str {
    RETURN "Decorated(" + SUPER.operation() + ")"
  }
}
```

### TypeScript
```typescript
interface Component {
  operation(): string;
}

class ConcreteComponent implements Component {
  operation(): string {
    return "ConcreteComponent";
  }
}

class Decorator implements Component {
  constructor(protected component: Component) {}
  
  operation(): string {
    return this.component.operation();
  }
}

class ConcreteDecorator extends Decorator {
  operation(): string {
    return `Decorated(${super.operation()})`;
  }
}

// Usage
const component = new ConcreteDecorator(
  new ConcreteDecorator(new ConcreteComponent())
);
```

### Rust
```rust
trait Component {
    fn operation(&self) -> String;
}

struct ConcreteComponent;
impl Component for ConcreteComponent {
    fn operation(&self) -> String {
        "ConcreteComponent".to_string()
    }
}

struct Decorator<T: Component> {
    component: T,
}

impl<T: Component> Component for Decorator<T> {
    fn operation(&self) -> String {
        self.component.operation()
    }
}

struct ConcreteDecorator<T: Component> {
    decorator: Decorator<T>,
}

impl<T: Component> Component for ConcreteDecorator<T> {
    fn operation(&self) -> String {
        format!("Decorated({})", self.decorator.operation())
    }
}
```

### Java
```java
interface Component {
    String operation();
}

class ConcreteComponent implements Component {
    public String operation() {
        return "ConcreteComponent";
    }
}

class Decorator implements Component {
    protected Component component;
    
    Decorator(Component component) {
        this.component = component;
    }
    
    public String operation() {
        return component.operation();
    }
}

class ConcreteDecorator extends Decorator {
    ConcreteDecorator(Component component) {
        super(component);
    }
    
    public String operation() {
        return "Decorated(" + super.operation() + ")";
    }
}
```

### Python
```python
from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def operation(self) -> str: pass

class ConcreteComponent(Component):
    def operation(self) -> str:
        return "ConcreteComponent"

class Decorator(Component):
    def __init__(self, component: Component):
        self._component = component
    
    def operation(self) -> str:
        return self._component.operation()

class ConcreteDecorator(Decorator):
    def operation(self) -> str:
        return f"Decorated({super().operation()})"
```

**When to use:**
- Add/remove responsibilities dynamically
- Extending functionality of final class
- When subclassing would produce explosion of classes

**Common use cases:**
- I/O streams (BufferedReader, etc.)
- Middleware chains
- UI component styling

---

## Facade

**Intent:** Provide unified interface to set of interfaces in subsystem  
**Use when:** Simplifying complex system for client use

### AI Pseudocode
```
CLASS Facade {
  -subsys1: Subsystem1
  -subsys2: Subsystem2
  -subsys3: Subsystem3
  
  CONSTRUCTOR() {
    this.subsys1 = NEW Subsystem1()
    this.subsys2 = NEW Subsystem2()
    this.subsys3 = NEW Subsystem3()
  }
  
  METHOD simpleOperation(): str {
    VAR result = ""
    result += this.subsys1.operation()
    result += this.subsys2.operation()
    result += this.subsys3.operation()
    RETURN result
  }
}
```

### TypeScript
```typescript
class Subsystem1 {
  operation(): string { return "Subsystem1 "; }
}

class Subsystem2 {
  operation(): string { return "Subsystem2 "; }
}

class Subsystem3 {
  operation(): string { return "Subsystem3"; }
}

class Facade {
  private subsys1 = new Subsystem1();
  private subsys2 = new Subsystem2();
  private subsys3 = new Subsystem3();
  
  simpleOperation(): string {
    return this.subsys1.operation() +
           this.subsys2.operation() +
           this.subsys3.operation();
  }
}
```

### Rust
```rust
struct Subsystem1;
impl Subsystem1 {
    fn operation(&self) -> String { "Subsystem1 ".to_string() }
}

struct Subsystem2;
impl Subsystem2 {
    fn operation(&self) -> String { "Subsystem2 ".to_string() }
}

struct Facade {
    subsys1: Subsystem1,
    subsys2: Subsystem2,
}

impl Facade {
    fn new() -> Self {
        Facade {
            subsys1: Subsystem1,
            subsys2: Subsystem2,
        }
    }
    
    fn simple_operation(&self) -> String {
        format!("{}{}",
            self.subsys1.operation(),
            self.subsys2.operation()
        )
    }
}
```

### Java
```java
class Subsystem1 {
    String operation() { return "Subsystem1 "; }
}

class Subsystem2 {
    String operation() { return "Subsystem2 "; }
}

class Facade {
    private Subsystem1 subsys1 = new Subsystem1();
    private Subsystem2 subsys2 = new Subsystem2();
    
    String simpleOperation() {
        return subsys1.operation() + subsys2.operation();
    }
}
```

### Python
```python
class Subsystem1:
    def operation(self) -> str:
        return "Subsystem1 "

class Subsystem2:
    def operation(self) -> str:
        return "Subsystem2 "

class Facade:
    def __init__(self):
        self._subsys1 = Subsystem1()
        self._subsys2 = Subsystem2()
    
    def simple_operation(self) -> str:
        return self._subsys1.operation() + self._subsys2.operation()
```

**When to use:**
- Provide simple interface to complex subsystem
- Decouple subsystem from clients and other subsystems
- Layer your subsystems

**Facade vs Adapter:**
- Facade simplifies a complex interface
- Adapter converts one interface to another

---

## Proxy

**Intent:** Provide placeholder/surrogate for another object to control access  

**Types:**
- **Remote Proxy:** Represent object in different address space
- **Virtual Proxy:** Create expensive object on demand (lazy loading)
- **Protection Proxy:** Control access permissions
- **Cache Proxy:** Cache results of expensive operations

### AI Pseudocode
```
INTERFACE Subject {
  FN request(): str
}

CLASS RealSubject IMPLEMENTS Subject {
  FN request(): str {
    // Expensive operation
    RETURN "RealSubject result"
  }
}

CLASS Proxy IMPLEMENTS Subject {
  -realSubject: RealSubject
  -cachedResult: str
  
  FN request(): str {
    IF this.cachedResult == null {
      IF this.realSubject == null {
        this.realSubject = NEW RealSubject()
      }
      this.cachedResult = this.realSubject.request()
    }
    RETURN this.cachedResult
  }
}
```

### TypeScript
```typescript
interface Subject {
  request(): string;
}

class RealSubject implements Subject {
  request(): string {
    // Expensive operation
    return "RealSubject result";
  }
}

class Proxy implements Subject {
  private realSubject?: RealSubject;
  private cachedResult?: string;
  
  request(): string {
    if (!this.cachedResult) {
      if (!this.realSubject) {
        this.realSubject = new RealSubject();
      }
      this.cachedResult = this.realSubject.request();
    }
    return this.cachedResult;
  }
}
```

### Rust
```rust
trait Subject {
    fn request(&self) -> String;
}

struct RealSubject;
impl Subject for RealSubject {
    fn request(&self) -> String {
        "RealSubject result".to_string()
    }
}

struct Proxy {
    real_subject: Option<RealSubject>,
    cached: Option<String>,
}

impl Subject for Proxy {
    fn request(&self) -> String {
        if let Some(ref cached) = self.cached {
            return cached.clone();
        }
        // In real impl, would need interior mutability
        "Cached or fetched".to_string()
    }
}
```

### Java
```java
interface Subject {
    String request();
}

class RealSubject implements Subject {
    public String request() {
        return "RealSubject result";
    }
}

class Proxy implements Subject {
    private RealSubject realSubject;
    private String cachedResult;
    
    public String request() {
        if (cachedResult == null) {
            if (realSubject == null) {
                realSubject = new RealSubject();
            }
            cachedResult = realSubject.request();
        }
        return cachedResult;
    }
}
```

### Python
```python
from abc import ABC, abstractmethod

class Subject(ABC):
    @abstractmethod
    def request(self) -> str: pass

class RealSubject(Subject):
    def request(self) -> str:
        return "RealSubject result"

class Proxy(Subject):
    def __init__(self):
        self._real_subject = None
        self._cached = None
    
    def request(self) -> str:
        if self._cached is None:
            if self._real_subject is None:
                self._real_subject = RealSubject()
            self._cached = self._real_subject.request()
        return self._cached
```

---

## Composite

**Intent:** Compose objects into tree structures to represent part-whole hierarchies  
**Use when:** Clients treat individual objects and compositions uniformly

### AI Pseudocode
```
INTERFACE Component {
  FN operation(): str
  FN add(c: Component): void
  FN remove(c: Component): void
}

CLASS Leaf IMPLEMENTS Component {
  FN operation(): str {
    RETURN "Leaf"
  }
  FN add(c: Component): void { /* no-op */ }
  FN remove(c: Component): void { /* no-op */ }
}

CLASS Composite IMPLEMENTS Component {
  -children: List<Component>
  
  FN operation(): str {
    VAR results = []
    FOR child IN this.children {
      results.add(child.operation())
    }
    RETURN results.join(", ")
  }
  
  FN add(c: Component): void {
    this.children.add(c)
  }
}
```

**When to use:**
- Tree structures (UI components, file systems, org charts)
- Ignore difference between compositions and individual objects