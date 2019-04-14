`package id.kawalc1.cli

import org.rogach.scallop.ScallopConf

class Tool[C <: ScallopConf](conf: C) {
  type Handler = C => Unit

  var subcmdHandlers = Map[ScallopConf, Handler]()
  var primaryHandler: Option[Handler] = None

  def registerSubcmdHandler(subcmd: ScallopConf, handler: Handler): Unit = {
    subcmdHandlers += (subcmd -> handler)
  }

  def registerPrimaryHandler(handler: Handler): Unit = {
    primaryHandler = Some(handler)
  }

  def run(): Unit = {
    conf.subcommand match {
      case None => conf.printHelp()
      case Some(cmd: ScallopConf) =>
        if (subcmdHandlers.keySet.contains(cmd)) {
          subcmdHandlers(cmd).apply(conf)
        } else {
          println(s"No Handler registered for ${cmd.printedName}!")
        }
    }
  }
}
