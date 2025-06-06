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
		builder = function()
			local input_file = vim.fn.input("Enter input XLSX file: ")
			return {
				cmd = { "poetry", "run", "fst", "translate", input_file },
			}
		end,
	},
	{
		name = "Run: Spread",
		builder = function()
			local input_file = vim.fn.input("Enter input Markdown file: ")
			return {
				cmd = { "poetry", "run", "fst", "spread", input_file },
			}
		end,
	},
}
