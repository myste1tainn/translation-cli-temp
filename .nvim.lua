return {
	{
		name = "Run",
		builder = function()
			local subcommand = vim.fn.input("Enter subcommand: ")
			local input_file = vim.fn.input("Enter input file: ")
			vim.notify(
				"Running Poetry with Fst subcommand: " .. subcommand .. " on file: " .. input_file,
				vim.log.levels.INFO
			)
			return {
				cmd = { "poetry", "run", "fst", subcommand, input_file },
			}
		end,
	},
	{
		name = "Run: Translate",
		params = function()
			local stdout = vim.system({ "find", "./data/", "-type", "f" }):wait().stdout
			local files = vim.split(stdout, "\n", { trimempty = true })
			return {
				input_file = {
					type = "enum",
					name = "input_fle",
					desc = "Select an input XLSX file to translate",
					default = "./data/ptt/PTTEP_Financial statement_TH_2567_Cut version.XLSX",
					-- Ensure the file is an XLSX file
					pattern = "%.xlsx$",
					choices = files,
				},
			}
		end,
		builder = function(params)
			return {
				cmd = { "poetry", "run", "fst", "translate", params.input_file },
			}
		end,
	},
	{
		name = "Run: Spread",
		params = function()
			local stdout = vim.system({ "find", "./out/" }):wait().stdout
			local files = vim.split(stdout, "\n", { trimempty = true })
			return {
				input_file = {
					type = "string",
					name = "input_file",
					desc = "Select an input Markdown to spread",
					default = "out/PTTEP_Financial statement_TH_2567_Cut version_translated.md",
					-- Ensure the file is an XLSX file
					pattern = "%.md$",
					choices = files,
				},
			}
		end,
		builder = function(params)
			return {
				cmd = { "poetry", "run", "fst", "spread", params.input_file },
			}
		end,
	},
}
