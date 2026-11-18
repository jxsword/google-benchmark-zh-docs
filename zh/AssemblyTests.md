---
upstream_file: AssemblyTests.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: 89df7ca520df857b43ff401a06463e14c06cb3d7
status: current
generated_by: agent
---

# 汇编测试

Benchmark 库提供了一些主要目的是影响汇编生成的函数，包括 `DoNotOptimize` 与 `ClobberMemory`。此外还有其他函数（如 `KeepRunning`），对这些函数而言生成良好的汇编至关重要。

对这些函数来说，必须有测试来验证实现的正确性与质量。这需要测试编译器生成的代码。

本文描述 Benchmark 库如何测试编译器输出，以及如何正确编写新测试。

## 测试剖析

编写测试分两步：

* 编写想要为其生成汇编的代码。
* 添加 `// CHECK` 行与验证过的汇编进行匹配。

示例：
```c++

// CHECK-LABEL: test_add:
extern "C" int test_add() {
    extern int ExternInt;
    return ExternInt + 1;

    // CHECK: movl ExternInt(%rip), %eax
    // CHECK: addl %eax
    // CHECK: ret
}

```

#### LLVM Filecheck

[LLVM 的 Filecheck](https://llvm.org/docs/CommandGuide/FileCheck.html)
用于把生成的汇编与测试源文件中指定的 `// CHECK` 行进行比对。如何编写 `CHECK` 指令，请参见上方链接的文档。

#### 技巧与窍门：

* 测试应只匹配建立正确性所需的最少输出。`CHECK` 指令不必匹配在上一个匹配之后的紧邻下一行，因此测试应省略对不重要的汇编片段的检查。（[`CHECK-NEXT`](https://llvm.org/docs/CommandGuide/FileCheck.html#the-check-next-directive)
可用于确保匹配恰好紧跟上一个匹配。）

* 测试以 `-O3 -g0` 编译。因此我们只测试优化后的输出。

* 汇编输出还会用 `tools/strip_asm.py` 进一步清理：在运行测试之前移除注释、汇编器指令与未使用的标签。

* 测试的生成并清理后的汇编文件输出在 `<build-directory>/test/<test-name>.s`

* Filecheck 支持[`CHECK` 前缀](https://llvm.org/docs/CommandGuide/FileCheck.html#cmdoption-check-prefixes)
来指定只在特定情况下匹配的行。Benchmark 测试用 `CHECK-CLANG` 与 `CHECK-GNU` 标注只期望匹配 Clang 或 GCC 输出的行。普通 `CHECK` 行对所有编译器匹配。（注意：`CHECK-NOT` 与 `CHECK-LABEL` 不是前缀——它们是非前缀 `CHECK` 行的变体）

* 用 `extern "C"` 对特定函数禁用名字修饰（name mangling）。这使它们在 `CHECK` 行中更易书写。

## 编写可移植测试的问题

编写检查编译器生成代码的测试天然不可移植。不同编译器甚至不同编译器版本可能生成完全不同的代码。Benchmark 测试必须容忍这一点。

LLVM Filecheck 提供了许多帮助编写“更可移植”测试的机制，包括[用正则表达式匹配](https://llvm.org/docs/CommandGuide/FileCheck.html#filecheck-pattern-matching-syntax)、
允许创建[命名变量](https://llvm.org/docs/CommandGuide/FileCheck.html#filecheck-variables)
供后续匹配，以及[检查非顺序匹配](https://llvm.org/docs/CommandGuide/FileCheck.html#the-check-dag-directive)。

#### 捕获变量

例如，假设 GCC 把变量存入寄存器而 Clang 存入内存。要写出对两种情形都容忍的测试，我们先“捕获”存储目标，然后用捕获到的表达式书写测试的其余部分。

```c++
// CHECK-LABEL: test_div_no_op_into_shr:
extern "C" void test_div_no_op_into_shr(int value) {
    int divisor = 2;
    benchmark::DoNotOptimize(divisor); // hide the value from the optimizer
    return value / divisor;

    // CHECK: movl $2, [[DEST:.*]]
    // CHECK: idivl [[DEST]]
    // CHECK: ret
}
```

#### 用正则表达式匹配不同的输出

测试常常需要检查在编译器或编译器版本之间有细微差异的汇编行。一个常见例子是匹配栈帧地址。此时可用正则表达式匹配输出中不同的部分。例如：

<!-- {% raw %} -->
```c++
int ExternInt;
struct Point { int x, y, z; };

// CHECK-LABEL: test_store_point:
extern "C" void test_store_point() {
    Point p{ExternInt, ExternInt, ExternInt};
    benchmark::DoNotOptimize(p);

    // CHECK: movl ExternInt(%rip), %eax
    // CHECK: movl %eax, -{{[0-9]+}}(%rsp)
    // CHECK: movl %eax, -{{[0-9]+}}(%rsp)
    // CHECK: movl %eax, -{{[0-9]+}}(%rsp)
    // CHECK: ret
}
```
<!-- {% endraw %} -->

## 现有要求与限制

测试要求构建机器的 `PATH` 位置安装了 Filecheck，否则测试将被禁用。

此外，如上一节所述，代码生成测试天然不可移植。目前测试限于：

* x86_64 目标。
* 以 GCC 或 Clang 编译

进一步的工作（至少在有限范围内）可以把测试扩展到其他架构与编译器（使用 `CHECK` 前缀）。

此外，对指定了会改变代码生成的附加 flag 的构建（包括 `--coverage` 或 `-fsanitize=`），测试会失败。
