# Creational Patterns

Patterns that deal with object creation mechanisms.

---

## Factory Method

**Intent:** Create objects without specifying exact class  
**Use when:** You don't know beforehand what types you'll need

### AI Pseudocode
```
CLASS Creator {
  ABSTRACT METHOD factoryMethod(): Product
  
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
```

### TypeScript
```typescript
interface Product {
  use(): void;
}

abstract class Creator {
  abstract factoryMethod(): Product;
  
  operation(): void {
    const product = this.factoryMethod();
    product.use();
  }
}

class ConcreteCreator extends Creator {
  factoryMethod(): Product {
    return new ConcreteProduct();
  }
}
```

### Rust
```rust
trait Product {
    fn use_product(&self);
}

trait Creator {
    fn factory_method(&self) -> Box<dyn Product>;
    
    fn operation(&self) {
        let product = self.factory_method();
        product.use_product();
    }
}

struct ConcreteCreator;
impl Creator for ConcreteCreator {
    fn factory_method(&self) -> Box<dyn Product> {
        Box::new(ConcreteProduct)
    }
}
```

### Java
```java
interface Product {
    void use();
}

abstract class Creator {
    abstract Product factoryMethod();
    
    void operation() {
        Product product = factoryMethod();
        product.use();
    }
}

class ConcreteCreator extends Creator {
    @Override
    Product factoryMethod() {
        return new ConcreteProduct();
    }
}
```

### Python
```python
from abc import ABC, abstractmethod

class Product(ABC):
    @abstractmethod
    def use(self): pass

class Creator(ABC):
    @abstractmethod
    def factory_method(self) -> Product: pass
    
    def operation(self):
        product = self.factory_method()
        product.use()

class ConcreteCreator(Creator):
    def factory_method(self) -> Product:
        return ConcreteProduct()
```

**When to use:**
- Class can't anticipate what objects it must create
- Class wants subclasses to specify objects
- Localize knowledge of helper class

**Common mistakes:**
- Using when simple instantiation suffices
- Over-abstracting with abstract factory when factory method is enough

---

## Abstract Factory

**Intent:** Create families of related objects  
**Use when:** You need multiple variants of products

### AI Pseudocode
```
INTERFACE GUIFactory {
  FN createButton(): Button
  FN createCheckbox(): Checkbox
}

CLASS WinFactory IMPLEMENTS GUIFactory {
  FN createButton(): Button { RETURN NEW WinButton() }
  FN createCheckbox(): Checkbox { RETURN NEW WinCheckbox() }
}

CLASS MacFactory IMPLEMENTS GUIFactory {
  FN createButton(): Button { RETURN NEW MacButton() }
  FN createCheckbox(): Checkbox { RETURN NEW MacCheckbox() }
}
```

**When to use vs Factory Method:**
- Factory Method = create ONE product
- Abstract Factory = create FAMILIES of related products

---

## Builder

**Intent:** Separate construction of complex object from its representation  
**Use when:** Object has MANY optional parameters or complex construction steps

### AI Pseudocode
```
CLASS Product {
  partA: str
  partB: str
  partC: str
}

CLASS Builder {
  -product: Product
  
  METHOD setPartA(v: str): Builder {
    this.product.partA = v
    RETURN this
  }
  
  METHOD setPartB(v: str): Builder {
    this.product.partB = v
    RETURN this
  }
  
  METHOD setPartC(v: str): Builder {
    this.product.partC = v
    RETURN this
  }
  
  METHOD build(): Product {
    RETURN this.product
  }
}

// Usage
VAR product = Builder().setPartA("A").setPartB("B").build()
```

### TypeScript
```typescript
class Product {
  partA?: string;
  partB?: string;
  partC?: string;
}

class Builder {
  private product = new Product();
  
  setPartA(value: string): this {
    this.product.partA = value;
    return this;
  }
  
  setPartB(value: string): this {
    this.product.partB = value;
    return this;
  }
  
  setPartC(value: string): this {
    this.product.partC = value;
    return this;
  }
  
  build(): Product {
    return this.product;
  }
}

// Usage
const product = new Builder()
  .setPartA("A")
  .setPartB("B")
  .build();
```

### Rust
```rust
struct Product {
    part_a: Option<String>,
    part_b: Option<String>,
    part_c: Option<String>,
}

struct Builder {
    product: Product,
}

impl Builder {
    fn new() -> Self {
        Builder {
            product: Product {
                part_a: None,
                part_b: None,
                part_c: None,
            },
        }
    }
    
    fn part_a(mut self, value: &str) -> Self {
        self.product.part_a = Some(value.to_string());
        self
    }
    
    fn part_b(mut self, value: &str) -> Self {
        self.product.part_b = Some(value.to_string());
        self
    }
    
    fn build(self) -> Product {
        self.product
    }
}

// Usage
let product = Builder::new()
    .part_a("A")
    .part_b("B")
    .build();
```

### Java
```java
public class Product {
    private String partA;
    private String partB;
    private String partC;
    
    public static class Builder {
        private Product product = new Product();
        
        public Builder partA(String value) {
            product.partA = value;
            return this;
        }
        
        public Builder partB(String value) {
            product.partB = value;
            return this;
        }
        
        public Product build() {
            return product;
        }
    }
}

// Usage
Product product = new Product.Builder()
    .partA("A")
    .partB("B")
    .build();
```

### Python
```python
class Product:
    def __init__(self):
        self.part_a = None
        self.part_b = None
        self.part_c = None

class Builder:
    def __init__(self):
        self._product = Product()
    
    def set_part_a(self, value: str):
        self._product.part_a = value
        return self
    
    def set_part_b(self, value: str):
        self._product.part_b = value
        return self
    
    def build(self) -> Product:
        return self._product

# Usage
product = Builder().set_part_a("A").set_part_b("B").build()
```

**When to use:**
- Avoid telescoping constructors
- Different representations of same construction process
- Object requires step-by-step construction

**When NOT to use:**
- Simple objects with few parameters
- Performance-critical code (builder adds overhead)

---

## Singleton

**Intent:** Ensure only one instance exists  
**Use when:** Exactly one instance needed, global access point

### AI Pseudocode
```
CLASS Singleton {
  -static instance: Singleton
  
  -CONSTRUCTOR() {}
  
  +static getInstance(): Singleton {
    IF this.instance == null {
      this.instance = NEW Singleton()
    }
    RETURN this.instance
  }
}
```

### TypeScript
```typescript
class Singleton {
  private static instance: Singleton;
  
  private constructor() {}
  
  static getInstance(): Singleton {
    if (!Singleton.instance) {
      Singleton.instance = new Singleton();
    }
    return Singleton.instance;
  }
}
```

### Rust
```rust
use std::sync::OnceLock;

struct Singleton {
    data: String,
}

impl Singleton {
    fn get_instance() -> &'static Singleton {
        static INSTANCE: OnceLock<Singleton> = OnceLock::new();
        INSTANCE.get_or_init(|| Singleton {
            data: String::from("initialized"),
        })
    }
}
```

### Java
```java
public class Singleton {
    private static Singleton instance;
    
    private Singleton() {}
    
    public static synchronized Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```

### Python
```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Alternatives to consider:**
- Module-level variables (in Python)
- Dependency injection
- Factory with instance tracking

**Anti-patterns:**
- Singleton Manager (god object)
- Testing nightmare (hidden global state)
- Premature singleton-ization

---

## Prototype

**Intent:** Create new objects by copying existing ones  
**Use when:** Classes to instantiate specified at runtime, avoiding subclass explosion

### AI Pseudocode
```
INTERFACE Prototype {
  FN clone(): Prototype
}

CLASS ConcretePrototype IMPLEMENTS Prototype {
  -data: any
  
  CONSTRUCTOR(source?: ConcretePrototype) {
    IF source {
      this.data = copy(source.data)
    }
  }
  
  FN clone(): Prototype {
    RETURN NEW ConcretePrototype(this)
  }
}
```

**When to use:**
- High cost of creating vs copying
- Similar objects differ only in configuration
- Avoid building parallel class hierarchies