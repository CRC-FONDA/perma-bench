#include "parallel_benchmark.hpp"

#include <csignal>

namespace {

volatile sig_atomic_t thread_error;
void thread_error_handler(int) { thread_error = 1; }

}  // namespace

namespace perma {

bool ParallelBenchmark::run() {
  signal(SIGSEGV, thread_error_handler);

  for (size_t bm_num = 0; bm_num < configs_.size(); ++bm_num) {
    for (size_t thread_index = 0; thread_index < configs_[bm_num].number_threads; thread_index++) {
      pools_[bm_num].emplace_back(&run_in_thread, &thread_configs_[bm_num][thread_index], std::ref(configs_[bm_num]));
    }
  }

  // wait for all threads
  for (std::vector<std::thread>& pool : pools_) {
    for (std::thread& thread : pool) {
      if (thread_error) {
        utils::print_segfault_error();
        return false;
      }
      thread.join();
    }
  }

  return true;
}

void ParallelBenchmark::create_data_files() {
  pmem_data_.push_back(create_pmem_data_file(configs_[0], memory_regions_[0]));
  pmem_data_.push_back(create_pmem_data_file(configs_[1], memory_regions_[1]));

  dram_data_.push_back(create_dram_data(configs_[0], configs_[0].dram_memory_range));
  dram_data_.push_back(create_dram_data(configs_[1], configs_[1].dram_memory_range));
}

void ParallelBenchmark::set_up() {
  pools_.resize(2);
  thread_configs_.resize(2);
  single_set_up(configs_[0], pmem_data_[0], dram_data_[0], executions_[0].get(), results_[0].get(), &pools_[0],
                &thread_configs_[0]);
  single_set_up(configs_[1], pmem_data_[1], dram_data_[1], executions_[1].get(), results_[1].get(), &pools_[1],
                &thread_configs_[1]);
}

nlohmann::json ParallelBenchmark::get_result_as_json() {
  nlohmann::json result;
  result["config"][benchmark_name_one_] = get_json_config(0);
  result["config"][benchmark_name_two_] = get_json_config(1);
  result["results"][benchmark_name_one_].update(results_[0]->get_result_as_json());
  result["results"][benchmark_name_two_].update(results_[1]->get_result_as_json());
  return result;
}

ParallelBenchmark::ParallelBenchmark(const std::string& benchmark_name, std::string first_benchmark_name,
                                     std::string second_benchmark_name, const BenchmarkConfig& first_config,
                                     const BenchmarkConfig& second_config,
                                     std::vector<std::unique_ptr<BenchmarkExecution>>&& executions,
                                     std::vector<std::unique_ptr<BenchmarkResult>>&& results)
    : Benchmark(benchmark_name, BenchmarkType::Parallel,
                std::vector<MemoryRegion>{
                    {utils::generate_random_file_name(first_config.pmem_directory), true, first_config.is_hybrid},
                    {utils::generate_random_file_name(second_config.pmem_directory), true, second_config.is_hybrid}},
                std::vector<BenchmarkConfig>{first_config, second_config}, std::move(executions), std::move(results)),
      benchmark_name_one_{std::move(first_benchmark_name)},
      benchmark_name_two_{std::move(second_benchmark_name)} {}

ParallelBenchmark::ParallelBenchmark(const std::string& benchmark_name, std::string first_benchmark_name,
                                     std::string second_benchmark_name, const BenchmarkConfig& first_config,
                                     const BenchmarkConfig& second_config,
                                     std::vector<std::unique_ptr<BenchmarkExecution>>&& executions,
                                     std::vector<std::unique_ptr<BenchmarkResult>>&& results,
                                     std::filesystem::path pmem_file_first)
    : Benchmark(benchmark_name, BenchmarkType::Parallel,
                std::vector<MemoryRegion>{
                    {{std::move(pmem_file_first), false, first_config.is_hybrid},
                     {utils::generate_random_file_name(second_config.pmem_directory), true, second_config.is_hybrid}}},
                std::vector<BenchmarkConfig>{first_config, second_config}, std::move(executions), std::move(results)),
      benchmark_name_one_{std::move(first_benchmark_name)},
      benchmark_name_two_{std::move(second_benchmark_name)} {}

ParallelBenchmark::ParallelBenchmark(const std::string& benchmark_name, std::string first_benchmark_name,
                                     std::string second_benchmark_name, const BenchmarkConfig& first_config,
                                     const BenchmarkConfig& second_config,
                                     std::vector<std::unique_ptr<BenchmarkExecution>>&& executions,
                                     std::vector<std::unique_ptr<BenchmarkResult>>&& results,
                                     std::filesystem::path pmem_file_first, std::filesystem::path pmem_file_second)
    : Benchmark(benchmark_name, BenchmarkType::Parallel,
                std::vector<MemoryRegion>{{{std::move(pmem_file_first), false, first_config.is_hybrid},
                                           {std::move(pmem_file_second), false, second_config.is_hybrid}}},
                std::vector<BenchmarkConfig>{first_config, second_config}, std::move(executions), std::move(results)),
      benchmark_name_one_{std::move(first_benchmark_name)},
      benchmark_name_two_{std::move(second_benchmark_name)} {}

const std::string& ParallelBenchmark::get_benchmark_name_one() const { return benchmark_name_one_; }

const std::string& ParallelBenchmark::get_benchmark_name_two() const { return benchmark_name_two_; }

}  // namespace perma
