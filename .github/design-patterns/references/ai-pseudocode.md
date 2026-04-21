# AI Pseudocode Format

A compact, language-agnostic syntax optimized for AI parsing and code generation.

## Syntax Rules

```
# Keywords: CLASS, INTERFACE, FN, METHOD, VAR, CONST, IF, ELSE, FOR, WHILE, RETURN, NEW, EXTENDS, IMPLEMENTS
# Types: inferred, use lowercase for primitives (int, str, bool, any)
# Generics: Container<T>
# Access: +public, -private, #protected (or omit for default)
# References: this, self, super
```

## Example Patterns in AI Pseudocode

### Observer
```
INTERFACE Observer {
  FN update(data: any): void
}

CLASS Subject {
  -observers: List<Observer>
  -state: any
  
  METHOD attach(o: Observer): void {
    this.observers.add(o)
  }
  
  METHOD detach(o: Observer): void {
    this.observers.remove(o)
  }
  
  METHOD notify(): void {
    FOR o IN this.observers {
      o.update(this.state)
    }
  }
  
  METHOD setState(s: any): void {
    this.state = s
    this.notify()
  }
}
```

### Strategy
```
INTERFACE Strategy {
  FN execute(data: any): any
}

CLASS Context {
  -strategy: Strategy
  
  METHOD setStrategy(s: Strategy): void {
    this.strategy = s
  }
  
  METHOD executeStrategy(data: any): any {
    RETURN this.strategy.execute(data)
  }
}

CLASS ConcreteStrategyA IMPLEMENTS Strategy {
  FN execute(data: any): any {
    RETURN sort_ascending(data)
  }
}
```

### Factory Method
```
CLASS Creator {
  # Factory method to override
  METHOD factoryMethod(): Product {
    THROW "Must implement"
  }
  
  METHOD operation(): void {
    VAR product = this.factoryMethod()
    product.use()
  }
}

CLASS ConcreteCreator EXTENDS Creator {
  METHOD factoryMethod(): Product {
    RETURN NEW ConcreteProduct()
  }
}

INTERFACE Product {
  FN use(): void
}
```

### Singleton
```
CLASS Singleton {
  -static instance: Singleton
  
  -CONSTRUCTOR() {}  // private
  
  +static getInstance(): Singleton {
    IF this.instance == null {
      this.instance = NEW Singleton()
    }
    RETURN this.instance
  }
}
```

### Builder
```
CLASS Builder {
  -product: Product
  
  CONSTRUCTOR() {
    this.product = NEW Product()
  }
  
  METHOD setPartA(value: any): Builder {
    this.product.partA = value
    RETURN this  // fluent
  }
  
  METHOD setPartB(value: any): Builder {
    this.product.partB = value
    RETURN this
  }
  
  METHOD build(): Product {
    RETURN this.product
  }
}
```

### Decorator
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

### Adapter
```
INTERFACE Target {
  FN request(): str
}

CLASS Adaptee {
  FN specificRequest(): str {
    RETURN "specific"
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

### Facade
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

### State
```
CLASS Context {
  -state: State
  
  METHOD setState(s: State): void {
    this.state = s
  }
  
  METHOD request(): void {
    this.state.handle(this)
  }
}

INTERFACE State {
  FN handle(ctx: Context): void
}

CLASS StateA IMPLEMENTS State {
  FN handle(ctx: Context): void {
    ctx.setState(NEW StateB())
  }
}

CLASS StateB IMPLEMENTS State {
  FN handle(ctx: Context): void {
    ctx.setState(NEW StateA())
  }
}
```

### Command
```
INTERFACE Command {
  FN execute(): void
  FN undo(): void
}

CLASS ConcreteCommand IMPLEMENTS Command {
  -receiver: Receiver
  -arg: any
  -prevState: any  // for undo
  
  CONSTRUCTOR(r: Receiver, a: any) {
    this.receiver = r
    this.arg = a
  }
  
  FN execute(): void {
    this.prevState = this.receiver.getState()
    this.receiver.action(this.arg)
  }
  
  FN undo(): void {
    this.receiver.setState(this.prevState)
  }
}
```

## Language Mapping Guide

### TypeScript
```
CLASS X EXTENDS Y → class X extends Y
INTERFACE X → interface X
METHOD → method (no function keyword inside class)
FN → function or arrow function
VAR/CONST → const/let
NEW → new
```

### Rust
```
CLASS X → struct X + impl X
EXTENDS → trait inheritance (rare) or composition
INTERFACE → trait
METHOD/FN → fn
VAR/CONST → let/const
NEW → StructName { ... }
OPTION<T> → Option<T>
```

### Java
```
CLASS X EXTENDS Y → class X extends Y
IMPLEMENTS → implements
INTERFACE → interface
METHOD/FN → method
VAR → var or explicit type
NEW → new
GENERICS<T> → <T>
```

### Python
```
CLASS X EXTENDS Y → class X(Y):
METHOD → def (self, ...)
FN → def
VAR → variable assignment
NEW → ClassName()
INTERFACE → Abstract Base Class or Protocol
```

## Compact Pattern Notation

For even more compact representation, use arrow notation:

```
# Observer
Subject -(attach, detach, notify)> Observer<update>

# Strategy
Context -(setStrategy)> Strategy<execute>

# Factory
Creator<abstract factoryMethod> -(creates)> Product

# Singleton
Singleton -getInstance> Singleton.instance

# Decorator
Decorator -(wraps)> Component -(extends)> ConcreteComponent

# Adapter
Adapter -(wraps)> Adaptee -(implements)> Target

# Facade
Facade -(aggregates)> [Subsystem1, Subsystem2, Subsystem3]
```

This compact notation captures the essential relationships in a single line.