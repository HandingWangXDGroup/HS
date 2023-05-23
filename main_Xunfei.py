from runner import Runner
from game import XunFeiGame
from common.arguments import get_common_args, get_coma_args, get_mixer_args, get_centralv_args, get_reinforce_args, get_commnet_args, get_g2anet_args


if __name__ == '__main__':
    for i in range(8):
        args = get_common_args()
        args = get_mixer_args(args)
        env = XunFeiGame()
        #env_info = env.get_env_info()
        args.n_actions = 5
        args.n_agents = 2
        args.state_shape = 3
        args.obs_shape = 3
        args.episode_limit = 50000
        runner = Runner(env, args)
        if not args.evaluate:
            runner.run(i)
        else:
            win_rate, _ = runner.evaluate()
            print('The win rate of {} is  {}'.format(args.alg, win_rate))
            break
        env.close()
