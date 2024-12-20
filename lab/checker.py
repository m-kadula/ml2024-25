import os
from typing import Callable, Tuple, List, Type

import numpy as np
import torch

import utils
from types import SimpleNamespace
from torch.optim import SGD
from torch.optim import Adagrad as torch_adagrad
from torch.optim import RMSprop as torch_rmsprop
from torch.optim import Adadelta as torch_adadelta
from torch.optim import Adam as torch_adam


def check_closest(fn: Callable) -> None:
    inputs = [
        (6, np.array([5, 3, 4])),
        (10, np.array([12, 2, 8, 9, 13, 14])),
        (-2, np.array([-5, 12, 6, 0, -14, 3])),
    ]
    assert np.isclose(fn(*inputs[0]), 5), "Jest błąd w funkcji closest!"
    assert np.isclose(fn(*inputs[1]), 9), "Jest błąd w funkcji closest!"
    assert np.isclose(fn(*inputs[2]), 0), "Jest błąd w funkcji closest!"


def check_poly(fn: Callable) -> None:
    inputs = [
        (6, np.array([5.5, 3, 4])),
        (10, np.array([12, 2, 8, 9, 13, 14])),
        (-5, np.array([6, 3, -12, 9, -15])),
    ]
    assert np.isclose(fn(*inputs[0]), 167.5), "Jest błąd w funkcji poly!"
    assert np.isclose(fn(*inputs[1]), 1539832), "Jest błąd w funkcji poly!"
    assert np.isclose(fn(*inputs[2]), -10809), "Jest błąd w funkcji poly!"


def check_multiplication_table(fn: Callable) -> None:
    inputs = [3, 5]
    assert np.all(
        fn(inputs[0]) == np.array([[1, 2, 3], [2, 4, 6], [3, 6, 9]])
    ), "Jest błąd w funkcji multiplication_table!"
    assert np.all(
        fn(inputs[1])
        == np.array(
            [
                [1, 2, 3, 4, 5],
                [2, 4, 6, 8, 10],
                [3, 6, 9, 12, 15],
                [4, 8, 12, 16, 20],
                [5, 10, 15, 20, 25],
            ]
        )
    ), "Jest błąd w funkcji multiplication_table!"


def check_1_1(
        mean_error: Callable,
        mean_squared_error: Callable,
        max_error: Callable,
        train_sets: List[np.ndarray],
) -> None:
    train_set_1d, train_set_2d, train_set_10d = train_sets
    assert np.isclose(mean_error(train_set_1d, np.array([8])), 8.897352)
    assert np.isclose(mean_error(train_set_2d, np.array([2.5, 5.2])), 7.89366)
    assert np.isclose(mean_error(train_set_10d, np.array(np.arange(10))), 14.16922)

    assert np.isclose(mean_squared_error(train_set_1d, np.array([3])), 23.03568)
    assert np.isclose(mean_squared_error(train_set_2d, np.array([2.4, 8.9])), 124.9397)
    assert np.isclose(mean_squared_error(train_set_10d, -np.arange(10)), 519.1699)

    assert np.isclose(max_error(train_set_1d, np.array([3])), 7.89418)
    assert np.isclose(max_error(train_set_2d, np.array([2.4, 8.9])), 14.8628)
    assert np.isclose(max_error(train_set_10d, -np.linspace(0, 5, num=10)), 23.1727)


def check_1_2(
        minimize_me: Callable, minimize_mse: Callable, minimize_max: Callable, train_set_1d: np.ndarray
) -> None:
    assert np.isclose(minimize_mse(train_set_1d), -0.89735)
    assert np.isclose(minimize_mse(train_set_1d * 2), -1.79470584)
    assert np.isclose(minimize_me(train_set_1d), -1.62603)
    assert np.isclose(minimize_me(train_set_1d ** 2), 3.965143)
    assert np.isclose(minimize_max(train_set_1d), 0.0152038)
    assert np.isclose(minimize_max(train_set_1d / 2), 0.007601903895526174)


def check_1_3(
        me_grad: Callable, mse_grad: Callable, max_grad: Callable, train_sets: List[np.ndarray]
) -> None:
    train_set_1d, train_set_2d, train_set_10d = train_sets
    assert all(np.isclose(me_grad(train_set_1d, np.array([0.99])), [0.46666667]))
    assert all(np.isclose(me_grad(train_set_2d, np.array([0.99, 8.44])), [0.21458924, 0.89772834]))
    assert all(
        np.isclose(
            me_grad(train_set_10d, np.linspace(0, 10, num=10)),
            [
                -0.14131273,
                -0.031631,
                0.04742431,
                0.0353542,
                0.16364242,
                0.23353252,
                0.30958123,
                0.35552034,
                0.4747464,
                0.55116738,
            ],
        )
    )

    assert all(np.isclose(mse_grad(train_set_1d, np.array([1.24])), [4.27470585]))
    assert all(
        np.isclose(mse_grad(train_set_2d, np.array([-8.44, 10.24])), [-14.25378235, 21.80373175])
    )
    assert all(np.isclose(max_grad(train_set_1d, np.array([5.25])), [1.0]))
    assert all(
        np.isclose(max_grad(train_set_2d, np.array([-6.28, -4.45])), [-0.77818704, -0.62803259])
    )


def check_02_linear_regression(lr_cls: Type) -> None:
    from sklearn import datasets

    np.random.seed(54)

    input_dataset = datasets.load_diabetes()
    lr = lr_cls()
    lr.fit(input_dataset.data, input_dataset.target)
    returned = lr.predict(input_dataset.data)
    expected = np.load(".checker/05/lr_diabetes.out.npz")["data"]
    assert np.allclose(expected, returned, rtol=1e-03, atol=1e-06), "Wrong prediction returned!"

    loss = lr.loss(input_dataset.data, input_dataset.target)
    assert np.isclose(
        loss, 26004.287402, rtol=1e-03, atol=1e-06
    ), "Wrong value of the loss function!"


def check_02_regularized_linear_regression(lr_cls: Type) -> None:
    from sklearn import datasets

    np.random.seed(54)

    input_dataset = datasets.load_diabetes()
    lr = lr_cls(lr=1e-2, alpha=1e-4)
    lr.fit(input_dataset.data, input_dataset.target)
    returned = lr.predict(input_dataset.data)
    # np.savez_compressed(".checker/05/rlr_diabetes.out.npz", data=returned)
    expected = np.load(".checker/05/rlr_diabetes.out.npz")["data"]
    assert np.allclose(expected, returned, rtol=1e-03, atol=1e-06), "Wrong prediction returned!"

    loss = lr.loss(input_dataset.data, input_dataset.target)
    assert np.isclose(
        loss, 26111.08336411, rtol=1e-03, atol=1e-06
    ), "Wrong value of the loss function!"


def check_4_1_mse(fn: Callable, datasets: List[Tuple[np.ndarray, np.ndarray]]) -> None:
    results = [torch.tensor(13.8520), torch.tensor(31.6952)]
    for (data, param), loss in zip(datasets, results):
        result = fn(data, param)
        assert torch.allclose(fn(data, param), loss, atol=1e-3), "Wrong loss returned!"


def check_4_1_me(fn: Callable, datasets: List[Tuple[np.ndarray, np.ndarray]]) -> None:
    results = [torch.tensor(3.6090), torch.tensor(5.5731)]
    for (data, param), loss in zip(datasets, results):
        assert torch.allclose(fn(data, param), loss, atol=1e-3), "Wrong loss returned!"


def check_4_1_max(fn: Callable, datasets: List[Tuple[np.ndarray, np.ndarray]]) -> None:
    results = [torch.tensor(7.1878), torch.tensor(7.5150)]
    for (data, param), loss in zip(datasets, results):
        assert torch.allclose(fn(data, param), loss, atol=1e-3), "Wrong loss returned!"


def check_4_1_lin_reg(fn: Callable, data: List[np.ndarray]) -> None:
    X, y, w = data
    assert torch.allclose(fn(X, w, y), torch.tensor(29071.6699), atol=1e-3), "Wrong loss returned!"


def check_4_1_reg_reg(fn: Callable, data: List[np.ndarray]) -> None:
    X, y, w = data
    assert torch.allclose(fn(X, w, y), torch.tensor(29073.4551)), "Wrong loss returned!"


def check_04_logistic_reg(lr_cls: Type) -> None:
    np.random.seed(10)
    torch.manual_seed(10)

    # **** First dataset ****
    input_dataset = utils.get_classification_dataset_1d()
    lr = lr_cls(1)
    lr.fit(input_dataset.data, input_dataset.target, lr=1e-3, num_steps=int(1e4))
    returned = lr.predict(input_dataset.data)
    save_path = ".checker/04/lr_dataset_1d.out.torch"
    # torch.save(returned, save_path)
    expected = torch.load(save_path)
    assert torch.allclose(expected, returned, rtol=1e-03, atol=1e-06), "Wrong prediction returned!"

    returned = lr.predict_proba(input_dataset.data)
    save_path = ".checker/04/lr_dataset_1d_proba.out.torch"
    # torch.save(returned, save_path)
    expected = torch.load(save_path)
    assert torch.allclose(expected, returned, rtol=1e-03, atol=1e-06), "Wrong prediction returned!"

    returned = lr.predict(input_dataset.data)
    save_path = ".checker/04/lr_dataset_1d_preds.out.torch"
    # torch.save(returned, save_path)
    expected = torch.load(save_path)
    assert torch.allclose(expected, returned, rtol=1e-03, atol=1e-06), "Wrong prediction returned!"

    # **** Second dataset ****
    input_dataset = utils.get_classification_dataset_2d()
    lr = lr_cls(2)
    lr.fit(input_dataset.data, input_dataset.target, lr=1e-2, num_steps=int(1e4))
    returned = lr.predict(input_dataset.data)
    save_path = ".checker/04/lr_dataset_2d.out.torch"
    # torch.save(returned, save_path)
    expected = torch.load(save_path)
    assert torch.allclose(expected, returned, rtol=1e-03, atol=1e-06), "Wrong prediction returned!"

    returned = lr.predict_proba(input_dataset.data)
    save_path = ".checker/04/lr_dataset_2d_proba.out.torch"
    # torch.save(returned, save_path)
    expected = torch.load(save_path)
    assert torch.allclose(expected, returned, rtol=1e-03, atol=1e-06), "Wrong prediction returned!"

    returned = lr.predict(input_dataset.data)
    save_path = ".checker/04/lr_dataset_2d_preds.out.torch"
    # torch.save(returned, save_path)
    expected = torch.load(save_path)
    assert torch.allclose(expected, returned, rtol=1e-03, atol=1e-06), "Wrong prediction returned!"


def optim_f(w: torch.Tensor) -> torch.Tensor:
    x = torch.tensor([0.2, 2], dtype=torch.float)
    return torch.sum(x * w ** 2)


def optim_g(w: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    x = torch.tensor([0.2, 2], dtype=torch.float)
    return torch.sum(x * w + b)


opt_checker_1 = SimpleNamespace(
    f=optim_f, params=[torch.tensor([-6, 2], dtype=torch.float, requires_grad=True)]
)
opt_checker_2 = SimpleNamespace(
    f=optim_g,
    params=[
        torch.tensor([-6, 2], dtype=torch.float, requires_grad=True),
        torch.tensor([1, -1], dtype=torch.float, requires_grad=True),
    ],
)

test_params = {
    "Momentum": {
        "torch_cls": SGD,
        "torch_params": {"lr": 0.1, "momentum": 0.9},
        "params": {"learning_rate": 0.1, "gamma": 0.9},
    },
    "Adagrad": {
        "torch_cls": torch_adagrad,
        "torch_params": {"lr": 0.5, "eps": 1e-8},
        "params": {"learning_rate": 0.5, "epsilon": 1e-8},
    },
    "RMSProp": {
        "torch_cls": torch_rmsprop,
        "torch_params": {
            "lr": 0.5,
            "alpha": 0.9,
            "eps": 1e-08,
        },
        "params": {"learning_rate": 0.5, "gamma": 0.9, "epsilon": 1e-8},
    },
    "Adadelta": {
        "torch_cls": torch_adadelta,
        "torch_params": {"rho": 0.9, "eps": 1e-1},
        "params": {"gamma": 0.9, "epsilon": 1e-1},
    },
    "Adam": {
        "torch_cls": torch_adam,
        "torch_params": {"lr": 0.5, "betas": (0.9, 0.999), "eps": 1e-08},
        "params": {"learning_rate": 0.5, "beta1": 0.9, "beta2": 0.999, "epsilon": 1e-8},
    },
}


def test_optimizer(optim_cls: Type, num_steps: int = 10) -> None:
    test_dict = test_params[optim_cls.__name__]

    for ns in [opt_checker_1, opt_checker_2]:
        torch_params = [p.clone().detach().requires_grad_(True) for p in ns.params]
        torch_opt = test_dict["torch_cls"](torch_params, **test_dict["torch_params"])
        for _ in range(num_steps):
            torch_opt.zero_grad()

            loss = ns.f(*torch_params)
            loss.backward()
            torch_opt.step()

        params = [p.clone().detach().requires_grad_(True) for p in ns.params]
        opt = optim_cls(params, **test_dict["params"])

        for _ in range(num_steps):
            opt.zero_grad()

            loss = ns.f(*params)
            loss.backward()
            opt.step()

        for p, tp in zip(params, torch_params):
            assert torch.allclose(p, tp)


def test_droput(dropout_cls: Type) -> None:
    drop = dropout_cls(0.5)
    drop.train()
    x = torch.randn(10, 30)
    out = drop(x)

    for row, orig_row in zip(out, x):
        zeros_in_row = torch.where(row == 0.0)[0]
        non_zeros_in_row = torch.where(row != 0.0)[0]
        non_zeros_scaled = (row[non_zeros_in_row] == 2 * orig_row[non_zeros_in_row]).all()
        assert len(zeros_in_row) > 0 and len(zeros_in_row) < len(row) and non_zeros_scaled

    drop_eval = dropout_cls(0.5)
    drop_eval.eval()
    x = torch.randn(10, 30)
    out_eval = drop_eval(x)

    for row in out_eval:
        zeros_in_row = len(torch.where(row == 0.0)[0])
        assert zeros_in_row == 0


def test_bn(bn_cls: Type) -> None:
    torch.manual_seed(42)
    bn = bn_cls(num_features=100)

    opt = torch.optim.SGD(bn.parameters(), lr=0.1)

    bn.train()
    x = torch.rand(20, 100)
    out = bn(x)

    assert out.mean().abs().item() < 1e-4
    assert abs(out.var().item() - 1) < 1e-1

    assert (bn.sigma != 1).all()
    assert (bn.mu != 1).all()

    loss = 1 - out.mean()
    loss.backward()
    opt.step()

    assert (bn.beta != 0).all()

    n_steps = 10

    for i in range(n_steps):
        x = torch.rand(20, 100)
        out = bn(x)
        loss = 1 - out.mean()
        loss.backward()
        opt.step()

    torch.manual_seed(43)
    test_x = torch.randn(20, 100)
    bn.eval()
    test_out = bn(test_x)

    assert abs(test_out.mean() + 0.5) < 1e-1


expected_mean_readout = torch.tensor(
    [[-0.0035, 0.0505, -0.2221, 0.1404, 0.1922, -0.3736, -0.0672, 0.0752,
      -0.0613, 0.0439, -0.1307, -0.0752, -0.0310, 0.0081, -0.0553, -0.1734],
     [-0.0054, -0.0144, -0.3113, 0.1665, 0.0738, -0.3303, 0.0420, 0.0668,
      0.0494, 0.2648, -0.0478, 0.0550, -0.1923, -0.0157, 0.0508, 0.0148],
     [-0.1912, 0.0309, -0.1512, 0.1283, 0.1120, -0.4540, -0.0644, 0.1378,
      -0.0194, 0.0103, -0.1713, 0.0175, -0.0604, -0.0193, -0.0208, -0.0822]]
)
expected_attention_readout = torch.Tensor(
    [[-0.0083, 0.0499, -0.2197, 0.1380, 0.1921, -0.3753, -0.0669, 0.0771,
      -0.0592, 0.0411, -0.1317, -0.0769, -0.0299, 0.0074, -0.0568, -0.1741],
     [-0.0068, -0.0131, -0.3102, 0.1656, 0.0736, -0.3312, 0.0410, 0.0670,
      0.0485, 0.2635, -0.0479, 0.0544, -0.1933, -0.0162, 0.0508, 0.0150],
     [-0.1911, 0.0308, -0.1514, 0.1271, 0.1100, -0.4542, -0.0658, 0.1376,
      -0.0215, 0.0099, -0.1723, 0.0164, -0.0618, -0.0209, -0.0217, -0.0817]],
)
expected_sage_layer_output = torch.tensor(
    [[-5.0965e-01, -4.5482e-01, -8.1451e-01, 5.4286e-03],
     [-5.6737e-01, -5.9137e-01, -7.9304e-01, 7.5955e-02],
     [-4.6768e-01, -5.0346e-01, -7.2765e-01, 5.0357e-02],
     [-6.4185e-01, -5.0983e-01, -8.6305e-01, 1.3008e-02],
     [-5.0465e-01, -3.5816e-01, -8.7864e-01, -3.1902e-02],
     [-5.6591e-01, -4.2403e-01, -8.7506e-01, 2.9357e-02],
     [-6.4185e-01, -5.0983e-01, -8.6305e-01, 1.3008e-02],
     [-5.7196e-01, -3.5674e-01, -9.4769e-01, -4.9931e-03],
     [-6.4185e-01, -5.0983e-01, -8.6305e-01, 1.3008e-02],
     [-5.2655e-01, -5.1094e-01, -8.3806e-01, -1.8521e-02],
     [-6.4185e-01, -5.0983e-01, -8.6305e-01, 1.3008e-02],
     [-5.7628e-01, -5.5394e-01, -8.7300e-01, -7.6976e-03],
     [-4.6768e-01, -5.0346e-01, -7.2765e-01, 5.0357e-02],
     [-5.4808e-01, -5.3204e-01, -7.8906e-01, 4.2878e-02],
     [-5.3417e-01, -3.5912e-01, -9.5030e-01, 2.3648e-05],
     [-6.2538e-01, -2.9249e-01, -1.1233e+00, 1.0970e-01],
     [-6.5214e-01, -3.8342e-01, -1.0136e+00, -1.6424e-02],
     [-6.5214e-01, -3.8342e-01, -1.0136e+00, -1.6424e-02]],
)
expected_gin_layer_output = torch.tensor(
    [[-0.4516, -0.3673, -0.5313, 0.3170],
     [-0.4524, -0.3760, -0.5243, 0.3249],
     [-0.4570, -0.3747, -0.5313, 0.3221],
     [-0.4763, -0.4030, -0.5390, 0.3335],
     [-0.4481, -0.3855, -0.5187, 0.3295],
     [-0.4545, -0.3838, -0.5245, 0.3276],
     [-0.4763, -0.4030, -0.5390, 0.3335],
     [-0.4390, -0.4001, -0.4973, 0.3446],
     [-0.4763, -0.4030, -0.5390, 0.3335],
     [-0.4683, -0.3882, -0.5400, 0.3248],
     [-0.4763, -0.4030, -0.5390, 0.3335],
     [-0.4682, -0.3921, -0.5374, 0.3277],
     [-0.4570, -0.3747, -0.5313, 0.3221],
     [-0.4225, -0.3671, -0.4928, 0.3295],
     [-0.3760, -0.3700, -0.4407, 0.3489],
     [-0.2646, -0.3342, -0.3357, 0.3683],
     [-0.3859, -0.3950, -0.4392, 0.3624],
     [-0.3859, -0.3950, -0.4392, 0.3624]],
)
expected_simple_mpnn_output = torch.tensor(
    [[-0.1990, -0.2007, -0.7749, -0.2355],
     [-0.5297, -0.4750, -0.8783, -0.0762],
     [-0.3664, -0.4155, -0.7463, -0.0573],
     [-0.5217, -0.3488, -0.9198, -0.1840],
     [0.1237, -0.0524, -0.5546, -0.1867],
     [-0.3597, -0.2378, -0.8626, -0.1551],
     [-0.5217, -0.3488, -0.9198, -0.1840],
     [-0.3358, -0.2634, -0.8318, -0.0586],
     [-0.5217, -0.3488, -0.9198, -0.1840],
     [-0.2175, -0.2724, -0.7910, -0.2460],
     [-0.5217, -0.3488, -0.9198, -0.1840],
     [-0.3758, -0.3293, -0.9195, -0.2665],
     [-0.3664, -0.4155, -0.7463, -0.0573],
     [-0.3907, -0.4223, -0.7682, -0.0586],
     [-0.2049, -0.2482, -0.7605, -0.0309],
     [-0.1718, 0.0814, -1.0231, -0.2095],
     [-0.3551, -0.2676, -0.8502, -0.0614],
     [-0.3551, -0.2676, -0.8502, -0.0614]]
)
expected_sum_readout = torch.tensor(
    [[-0.0451, 0.6570, -2.8874, 1.8256, 2.4987, -4.8573, -0.8733, 0.9780,
      -0.7967, 0.5701, -1.6988, -0.9777, -0.4033, 0.1053, -0.7191, -2.2545],
     [-0.0268, -0.0720, -1.5565, 0.8324, 0.3692, -1.6515, 0.2101, 0.3342,
      0.2468, 1.3238, -0.2389, 0.2752, -0.9615, -0.0785, 0.2541, 0.0741],
     [-0.9559, 0.1545, -0.7560, 0.6414, 0.5598, -2.2701, -0.3222, 0.6888,
      -0.0969, 0.0516, -0.8565, 0.0875, -0.3022, -0.0964, -0.1039, -0.4109]],
)
expected_gine_layer_output = torch.tensor(
    [[-0.4519, -0.3654, -0.5197, 0.3193],
     [-0.4577, -0.3681, -0.5309, 0.3200],
     [-0.4617, -0.3697, -0.5356, 0.3193],
     [-0.4318, -0.3586, -0.5039, 0.3215],
     [-0.3675, -0.3206, -0.4476, 0.3215],
     [-0.4474, -0.3725, -0.5134, 0.3252],
     [-0.4318, -0.3586, -0.5039, 0.3215],
     [-0.4617, -0.3816, -0.5311, 0.3244],
     [-0.4318, -0.3586, -0.5039, 0.3215],
     [-0.3174, -0.2810, -0.4102, 0.3140],
     [-0.4318, -0.3586, -0.5039, 0.3215],
     [-0.3173, -0.2847, -0.4078, 0.3168],
     [-0.4617, -0.3697, -0.5356, 0.3193],
     [-0.4367, -0.3529, -0.5122, 0.3167],
     [-0.4103, -0.3570, -0.4806, 0.3282],
     [-0.4105, -0.3539, -0.4767, 0.3282],
     [-0.4575, -0.3899, -0.5207, 0.3318],
     [-0.4575, -0.3899, -0.5207, 0.3318]]
)
expected_gat_output = torch.tensor(
    [[0.2640, 0.0480, 0.0950, -0.0174, -0.2840, 0.0064, 0.0522, -0.1773,
      0.1720, 0.1878, -0.1340, 0.0229],
     [0.1955, 0.0230, 0.0520, 0.0308, -0.2525, 0.0519, 0.0259, -0.1553,
      0.1808, 0.1965, -0.1323, 0.0663],
     [0.2423, 0.0486, 0.1118, -0.0467, -0.2726, 0.0444, 0.0325, -0.1617,
      0.1654, 0.1770, -0.1465, 0.0071],
     [0.2717, 0.0307, 0.0516, 0.1657, -0.2802, -0.1184, 0.1700, -0.1849,
      0.2089, 0.2373, -0.1915, -0.0212],
     [0.2887, -0.0457, 0.2075, 0.0216, -0.2877, -0.0890, 0.1351, -0.1585,
      0.2169, 0.1446, -0.0779, 0.0065],
     [0.2594, -0.0098, 0.0917, 0.0416, -0.2764, -0.0409, 0.1162, -0.1622,
      0.1887, 0.1710, -0.1145, 0.0457],
     [0.2717, 0.0307, 0.0516, 0.1657, -0.2802, -0.1184, 0.1700, -0.1849,
      0.2089, 0.2373, -0.1915, -0.0212],
     [0.2488, -0.0431, 0.1990, 0.0435, -0.2735, -0.0590, 0.0793, -0.1624,
      0.2314, 0.1686, -0.0642, 0.0281],
     [0.2717, 0.0307, 0.0516, 0.1657, -0.2802, -0.1184, 0.1700, -0.1849,
      0.2089, 0.2373, -0.1915, -0.0212],
     [0.2924, 0.0171, 0.0866, 0.1376, -0.2914, -0.1295, 0.1688, -0.1878,
      0.2136, 0.2186, -0.1574, -0.0087],
     [0.2717, 0.0307, 0.0516, 0.1657, -0.2802, -0.1184, 0.1700, -0.1849,
      0.2089, 0.2373, -0.1915, -0.0212],
     [0.2485, 0.0049, 0.0737, 0.1471, -0.2700, -0.0880, 0.1455, -0.1686,
      0.2142, 0.2180, -0.1624, 0.0050],
     [0.2423, 0.0486, 0.1118, -0.0467, -0.2726, 0.0444, 0.0325, -0.1617,
      0.1654, 0.1770, -0.1465, 0.0071],
     [0.1620, 0.0681, 0.0655, -0.0755, -0.2404, 0.0517, -0.0479, -0.1210,
      0.1310, 0.2535, -0.1107, 0.0330],
     [0.1185, -0.0203, 0.1807, -0.1225, -0.2394, 0.0383, -0.0468, -0.0771,
      0.1557, 0.2144, -0.0754, 0.0079],
     [0.1485, -0.0095, 0.1458, -0.0414, -0.2376, 0.0539, -0.0255, -0.1200,
      0.1828, 0.2043, -0.0969, 0.0238],
     [0.1268, -0.0224, 0.1846, -0.0438, -0.2185, 0.0215, -0.0412, -0.0883,
      0.1823, 0.2223, -0.0525, 0.0223],
     [0.1268, -0.0224, 0.1846, -0.0438, -0.2185, 0.0215, -0.0412, -0.0883,
      0.1823, 0.2223, -0.0525, 0.0223]]
)
expected_dot_attention_output = torch.tensor(
    [[[0.247395, 0.028085, 0.077167, 0.078323, -0.272530, -0.039541,
       0.097621, -0.173803, 0.194980, 0.212308, -0.155935, 0.009429],
      [0.247197, 0.028359, 0.076629, 0.078957, -0.272447, -0.039580,
       0.097599, -0.173896, 0.195020, 0.212726, -0.156340, 0.009328],
      [0.247197, 0.028359, 0.076629, 0.078957, -0.272447, -0.039580,
       0.097599, -0.173896, 0.195020, 0.212726, -0.156340, 0.009328],
      [0.247205, 0.028425, 0.076465, 0.079172, -0.272451, -0.039678,
       0.097692, -0.173931, 0.195030, 0.212829, -0.156458, 0.009298],
      [0.247366, 0.028181, 0.077058, 0.078077, -0.272529, -0.039312,
       0.097431, -0.173821, 0.194880, 0.212299, -0.155915, 0.009523],
      [0.247294, 0.028266, 0.076776, 0.078823, -0.272488, -0.039640,
       0.097682, -0.173873, 0.195015, 0.212599, -0.156228, 0.009356],
      [0.247205, 0.028425, 0.076465, 0.079172, -0.272451, -0.039678,
       0.097692, -0.173931, 0.195030, 0.212829, -0.156458, 0.009298],
      [0.247267, 0.028328, 0.076711, 0.078774, -0.272479, -0.039554,
       0.097609, -0.173882, 0.194982, 0.212625, -0.156263, 0.009363],
      [0.247205, 0.028425, 0.076465, 0.079172, -0.272451, -0.039678,
       0.097692, -0.173931, 0.195030, 0.212829, -0.156458, 0.009298],
      [0.247439, 0.028163, 0.077091, 0.078058, -0.272561, -0.039385,
       0.097505, -0.173831, 0.194878, 0.212268, -0.155892, 0.009516],
      [0.247205, 0.028425, 0.076465, 0.079172, -0.272451, -0.039678,
       0.097692, -0.173931, 0.195030, 0.212829, -0.156458, 0.009298],
      [0.247439, 0.028163, 0.077091, 0.078058, -0.272561, -0.039385,
       0.097505, -0.173831, 0.194878, 0.212268, -0.155892, 0.009516],
      [0.247197, 0.028359, 0.076629, 0.078957, -0.272447, -0.039580,
       0.097599, -0.173896, 0.195020, 0.212726, -0.156340, 0.009328]],

     [[0.149018, -0.009261, 0.146324, -0.040262, -0.237542, 0.053946,
       -0.025190, -0.120178, 0.182961, 0.204468, -0.097441, 0.023849],
      [0.148795, -0.009539, 0.146771, -0.040582, -0.237508, 0.053813,
       -0.025267, -0.119906, 0.182963, 0.204425, -0.097220, 0.023744],
      [0.148841, -0.009706, 0.146875, -0.040337, -0.237519, 0.053888,
       -0.025151, -0.120024, 0.183147, 0.204257, -0.097275, 0.023751],
      [0.148969, -0.009118, 0.146230, -0.040569, -0.237560, 0.053904,
       -0.025295, -0.120064, 0.182772, 0.204599, -0.097426, 0.023824],
      [0.148969, -0.009118, 0.146230, -0.040569, -0.237560, 0.053904,
       -0.025295, -0.120064, 0.182772, 0.204599, -0.097426, 0.023824],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]]]
)
sub_optimal_multihead_attention_output = torch.tensor(
    [[[-0.047262, 0.158078, -0.034781, -0.059588, -0.184203, 0.316856,
       -0.051797, -0.067320, 0.136281, 0.157510, -0.516869, -0.168178],
      [-0.047338, 0.158081, -0.034847, -0.059696, -0.184200, 0.316798,
       -0.051846, -0.067277, 0.136283, 0.157549, -0.516819, -0.168149],
      [-0.047338, 0.158081, -0.034847, -0.059696, -0.184200, 0.316798,
       -0.051846, -0.067277, 0.136283, 0.157549, -0.516819, -0.168149],
      [-0.047268, 0.158293, -0.035019, -0.059606, -0.184036, 0.316881,
       -0.051766, -0.067249, 0.136248, 0.157471, -0.516841, -0.168100],
      [-0.047252, 0.158166, -0.034837, -0.059572, -0.184190, 0.316919,
       -0.051814, -0.067332, 0.136266, 0.157541, -0.516920, -0.168195],
      [-0.047393, 0.158178, -0.035001, -0.059744, -0.184167, 0.316858,
       -0.051927, -0.067270, 0.136275, 0.157615, -0.516819, -0.168113],
      [-0.047268, 0.158293, -0.035019, -0.059606, -0.184036, 0.316881,
       -0.051766, -0.067249, 0.136248, 0.157471, -0.516841, -0.168100],
      [-0.047321, 0.158228, -0.034976, -0.059684, -0.184134, 0.316867,
       -0.051861, -0.067273, 0.136249, 0.157590, -0.516864, -0.168169],
      [-0.047268, 0.158293, -0.035019, -0.059606, -0.184036, 0.316881,
       -0.051766, -0.067249, 0.136248, 0.157471, -0.516841, -0.168100],
      [-0.047309, 0.158097, -0.034834, -0.059547, -0.184185, 0.316923,
       -0.051868, -0.067345, 0.136356, 0.157493, -0.516793, -0.168035],
      [-0.047268, 0.158293, -0.035019, -0.059606, -0.184036, 0.316881,
       -0.051766, -0.067249, 0.136248, 0.157471, -0.516841, -0.168100],
      [-0.047309, 0.158097, -0.034834, -0.059547, -0.184185, 0.316923,
       -0.051868, -0.067345, 0.136356, 0.157493, -0.516793, -0.168035],
      [-0.047338, 0.158081, -0.034847, -0.059696, -0.184200, 0.316798,
       -0.051846, -0.067277, 0.136283, 0.157549, -0.516819, -0.168149]],

     [[-0.065048, 0.168032, -0.084588, -0.057781, -0.217642, 0.305161,
       -0.096480, -0.093513, 0.154069, 0.215230, -0.510000, -0.149824],
      [-0.065092, 0.168042, -0.084506, -0.057821, -0.217695, 0.305299,
       -0.096637, -0.093606, 0.154123, 0.215237, -0.510100, -0.149899],
      [-0.065017, 0.168049, -0.084602, -0.057950, -0.217689, 0.305254,
       -0.096547, -0.093616, 0.154084, 0.215219, -0.510125, -0.149970],
      [-0.065047, 0.168035, -0.084817, -0.057796, -0.217683, 0.305158,
       -0.096428, -0.093492, 0.153998, 0.215284, -0.509987, -0.149702],
      [-0.065047, 0.168035, -0.084817, -0.057796, -0.217683, 0.305158,
       -0.096428, -0.093492, 0.153998, 0.215284, -0.509987, -0.149702],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
      [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
       0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]]]
)
expected_multihead_attention_output = torch.tensor([
    [[-0.117051, -0.256190, -0.029193, -0.194455, -0.088500, -0.113039,
      -0.170806, -0.136658, 0.262097, 0.150990, -0.173398, -0.040790],
     [-0.117170, -0.256051, -0.028961, -0.194294, -0.088437, -0.113035,
      -0.171108, -0.136485, 0.262386, 0.150987, -0.173508, -0.040610],
     [-0.117170, -0.256051, -0.028961, -0.194294, -0.088437, -0.113035,
      -0.171108, -0.136485, 0.262386, 0.150987, -0.173508, -0.040610],
     [-0.117099, -0.255992, -0.028861, -0.194269, -0.088363, -0.113058,
      -0.171416, -0.136481, 0.262535, 0.150846, -0.173580, -0.040517],
     [-0.117058, -0.256067, -0.029084, -0.194431, -0.088473, -0.113060,
      -0.170990, -0.136549, 0.262198, 0.150907, -0.173536, -0.040652],
     [-0.117122, -0.256024, -0.028993, -0.194334, -0.088414, -0.113060,
      -0.171201, -0.136516, 0.262410, 0.150940, -0.173504, -0.040577],
     [-0.117099, -0.255992, -0.028861, -0.194269, -0.088363, -0.113058,
      -0.171416, -0.136481, 0.262535, 0.150846, -0.173580, -0.040517],
     [-0.117055, -0.256094, -0.029112, -0.194419, -0.088446, -0.113020,
      -0.171043, -0.136624, 0.262266, 0.150970, -0.173486, -0.040711],
     [-0.117099, -0.255992, -0.028861, -0.194269, -0.088363, -0.113058,
      -0.171416, -0.136481, 0.262535, 0.150846, -0.173580, -0.040517],
     [-0.117128, -0.255967, -0.029090, -0.194426, -0.088463, -0.113091,
      -0.171057, -0.136491, 0.262278, 0.150960, -0.173523, -0.040562],
     [-0.117099, -0.255992, -0.028861, -0.194269, -0.088363, -0.113058,
      -0.171416, -0.136481, 0.262535, 0.150846, -0.173580, -0.040517],
     [-0.117128, -0.255967, -0.029090, -0.194426, -0.088463, -0.113091,
      -0.171057, -0.136491, 0.262278, 0.150960, -0.173523, -0.040562],
     [-0.117170, -0.256051, -0.028961, -0.194294, -0.088437, -0.113035,
      -0.171108, -0.136485, 0.262386, 0.150987, -0.173508, -0.040610]],

    [[-0.150472, -0.234370, -0.056415, -0.185859, -0.108691, -0.107598,
      -0.092175, -0.105653, 0.253021, 0.206729, -0.169479, -0.021557],
     [-0.150440, -0.234546, -0.056519, -0.185783, -0.108668, -0.107720,
      -0.092035, -0.105673, 0.252905, 0.206662, -0.169275, -0.021583],
     [-0.150364, -0.234564, -0.056556, -0.185850, -0.108622, -0.107725,
      -0.092114, -0.105784, 0.252845, 0.206556, -0.169246, -0.021672],
     [-0.150413, -0.234456, -0.056422, -0.185877, -0.108677, -0.107593,
      -0.092118, -0.105623, 0.252939, 0.206553, -0.169372, -0.021544],
     [-0.150413, -0.234456, -0.056422, -0.185877, -0.108677, -0.107593,
      -0.092118, -0.105623, 0.252939, 0.206553, -0.169372, -0.021544],
     [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
      0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
     [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
      0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
     [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
      0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
     [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
      0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
     [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
      0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
     [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
      0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
     [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
      0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
     [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
      0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]]],
)
