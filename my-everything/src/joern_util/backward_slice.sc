import io.shiftleft.codepropertygraph.Cpg
import io.shiftleft.semanticcpg.language._
import io.shiftleft.codepropertygraph.cpgloading.{CpgLoader, CpgLoaderConfig}
import java.nio.file.{Files, Paths}

def backwardSlice(cpg: Cpg, variable: String, line: Int): Set[String] = {
  var slice: Set[String] = Set()

  def findDependencies(varName: String, idx: Long): Unit = {
    val assignments = cpg.assignment.filter(a => a.argument(1).code.contains(varName) && a.id < idx).l
    println(s"Found ${assignments.size} assignments for variable $varName")
    for (assignment <- assignments) {
      val codeLine = assignment.code
      println(s"Adding assignment to slice: $codeLine")
      slice += codeLine
      val rhs = assignment.argument(2).code.mkString("")
      findDependencies(rhs, assignment.id)
    }
    val calls = cpg.call.filter(c => c.argument.code.contains(varName) && c.id < idx).l
    println(s"Found ${calls.size} calls with variable $varName")
    for (call <- calls) {
      val codeLine = call.code
      println(s"Adding call to slice: $codeLine")
      slice += codeLine
      for (arg <- call.argument.l) {
        findDependencies(arg.code, call.id)
      }
    }
  }

  val targetAssignments = cpg.assignment.filter(a => a.lineNumber.contains(line) && a.argument(1).code.contains(variable)).l
  val targetCalls = cpg.call.filter(c => c.lineNumber.contains(line) && c.argument.code.contains(variable)).l

  println(s"Found ${targetAssignments.size} target assignments at line $line")
  for (assignment <- targetAssignments) {
    println(s"Processing assignment: ${assignment.code}")
    findDependencies(variable, assignment.id)
  }

  println(s"Found ${targetCalls.size} target calls at line $line")
  for (call <- targetCalls) {
    println(s"Processing call: ${call.code}")
    for (arg <- call.argument.l) {
      findDependencies(arg.code, call.id)
    }
  }

  slice
}

@main def exec(cpgFile: String, variable: String, line: Int, outFile: String): Unit = {
  importCpg(cpgFile)

  val slice = backwardSlice(cpg, variable, line)
  val output = slice.mkString("\n")

  println("Backward Slice:")
  println(output)

  Files.write(Paths.get(outFile), output.getBytes)
}
