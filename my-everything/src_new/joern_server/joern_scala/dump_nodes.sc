@main def exec(cpgFile: String, outFile: String) = {
   importCpg(cpgFile)
   cpg.all.toJson |> outFile
}

// run example
// joern --script /app/slicing-snapvuln/my-everything/src_new/joern_server/joern_scala/dump_nodes.sc --param cpgFile="/app/slicing-snapvuln/cpg.bin" --param outFile="output.json"